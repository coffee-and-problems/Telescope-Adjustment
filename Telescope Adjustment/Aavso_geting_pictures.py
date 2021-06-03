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
    PARAMS = {'ra':ra, 'dec':dec, 'maglimit':maglimit, 'fov':fov,
              'dss':'True', 'special':'std_field', 'std_field':'on',
              'north':'up', 'east':'right'}
    return requests.get(url = URL, params = PARAMS)

def GetPictureURL(response):
    soup = BeautifulSoup(response.text)

    img_responsive = soup.find_all("img", class_="img-responsive")
    
    if len(img_responsive) == 0:
        return None
    return domen + img_responsive[0].attrs['src']

def GetPicture(ra, dec):
    response = SendRequest(ra, dec)
    picture_url = GetPictureURL(response)
    if picture_url is None:
        return None
    return requests.get(url = picture_url).content

def crop_image(picture):
    _pil = Image.open(io.BytesIO(picture))
    return _pil.crop((17, 180, 1183, 1350))

def Save(object_name, picture):
    file_path = path.join("Fields", "{0}.png".format(object_name))
    crop_image(picture).save(file_path)


source_file = "test_coords.csv"
#source_file = "objects_coords.csv"

with open(source_file) as file:
    reader = csv.reader(file, skipinitialspace=True)
    next(reader, None)
    for source in reader:
        field = GetPicture(source[1], source[2])
        if field is None:
            print("No field found for {0}".format(source[0])) #сделать нормальное логирование

        Save(source[0], field)

