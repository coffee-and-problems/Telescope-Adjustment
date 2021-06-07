import requests
import csv
from os import path
from bs4 import BeautifulSoup
from PIL import Image
import io

#убрать в класс
domen = "https://app.aavso.org"
URL = "https://app.aavso.org/vsp/chart"
maglimit = '20.0'
fov = 15.0

def SendRequest(ra, dec):
    """
    Sends a request to https://app.aavso.org to get information on a specific object.
        :param ra: RA of the object (ex. 18 06 50.7 or 18:26:15.0)
        :type ra: string
        :param dec: dec of the object (ex. +69 49 28 or -14:51:00)
        :type dec: string
    """
    PARAMS = {'ra':ra, 'dec':dec, 'maglimit':maglimit, 'fov':fov,
              'dss':'True', 'special':'std_field', 'std_field':'on',
              'north':'up', 'east':'right'}
    return requests.get(url = URL, params = PARAMS)

def GetPictureURL(response):
    """
    Parses a response for an immage URL. If multiple, the first image will be used.
        :param response: http response from aavso web cite
        :type response: requests.models.Response
    """
    soup = BeautifulSoup(response.text)

    img_responsive = soup.find_all("img", class_="img-responsive")
    
    if len(img_responsive) == 0:
        return None
    return domen + img_responsive[0].attrs['src']

def GetField(obj_name, ra, dec):
    """
    Returns DSS field of view of the coords specified
        :param obj_name: name of the object
        :type ra: string
        :param ra: RA of the object (ex. 18 06 50.7 or 18:26:15.0)
        :type ra: string
        :param dec: dec of the object (ex. +69 49 28 or -14:51:00)
        :type dec: string
    """
    response = SendRequest(ra, dec)
    picture_url = GetPictureURL(response)
    if picture_url is None:
        print("No field found for {0}".format(obj_name)) #сделать нормальное логирование
        return None
    return Crop_image(requests.get(url = picture_url).content)

def Crop_image(picture):
    """
    Returns only field of view from aavso image
        :param picture: the image
        :type picture: bytes string
    """
    _pil = Image.open(io.BytesIO(picture))
    return _pil.crop((19, 182, 1183, 1350))

def Save(object_name, picture):
    """
    Saves pictures in "Fields" directory
        :param object_name: name of a file to be created
        :type object_name: string
        :param picture: the FOV to be saved
        :type picture: PIL.Image.Image
    """
    file_path = path.join("Fields", "{0}.png".format(object_name))
    picture.save(file_path)


source_file = "test_coords.csv"
#source_file = "objects_coords.csv"

with open(source_file) as file:
    reader = csv.reader(file, skipinitialspace=True)
    next(reader, None)
    for source in reader:
        field = GetField(source[0], source[1], source[2])
        if field is not None:
            Save(source[0], field)

