import requests
import csv
from os import path
from bs4 import BeautifulSoup
from PIL import Image
import io

class Aavso:
    """Provides interfaces to get data from app.aavso.org"""
    def __init__(self, *args, **kwargs):
        self.domen = "https://app.aavso.org"
        self.chart_url = "https://app.aavso.org/vsp/chart"
        self.maglimit = '20.0'

    def SendRequest(self, ra, dec, dss=False):
        """
        Sends a request to https://app.aavso.org to get information on a specific object.
            :param ra: RA of the object (ex. 18 06 50.7 or 18:26:15.0)
            :type ra: string
            :param dec: dec of the object (ex. +69 49 28 or -14:51:00)
            :type dec: string
            :param dss: if True, DSS field will be requested instead of AAVSO one
            :type dss: bool
        """
        PARAMS = {'ra':ra, 'dec':dec, 'maglimit':self.maglimit, 'fov':'9.5',
                      'scale':'F', 'type':'chart', 'orientation':'ccd',
                      'special':'std_field', 'std_field':'on',
                      'north':'up', 'east':'right', 'resolution':'75'}
        if dss:
            PARAMS['orientation'] = 'visual'
            PARAMS['dss'] = 'True'
        
        return requests.get(url = self.chart_url, params = PARAMS)

    def GetPictureURL(self, response):
        """
        Parses a response for an immage url. If multiple, the first image will be used.
            :param response: http response from aavso web cite
            :type response: requests.models.Response
        """
        soup = BeautifulSoup(response.text)

        img_responsive = soup.find_all("img", class_="img-responsive")
    
        if len(img_responsive) == 0:
            return None
        return self.domen + img_responsive[0].attrs['src']

    def GetField(self, obj_name, ra, dec, dss=False):
        """
        Returns DSS or AAVSO field of view of the coords specified
            :param obj_name: name of the object
            :type obj_name: string
            :param ra: RA of the object (ex. 18 06 50.7 or 18:26:15.0)
            :type ra: string
            :param dec: dec of the object (ex. +69 49 28 or -14:51:00)
            :type dec: string
            :param dss: if True, DSS field will be requested instead of AAVSO one
            :type dss: bool
        """
        response = self.SendRequest(ra, dec, dss)
        picture_url = self.GetPictureURL(response)
        if picture_url is None:
            print("No field found for {0}".format(obj_name)) #сделать нормальное логирование
            return None
        return self.Crop_image(requests.get(url = picture_url).content)

    def Crop_image(self, picture):
        """
        Returns only field of view from aavso image
            :param picture: the image
            :type picture: bytes string
        """
        _pil = Image.open(io.BytesIO(picture))
        return _pil.crop((8, 92, 592, 673))

    def Save(self, object_name, picture):
        """
        Saves pictures in "Fields" directory
            :param object_name: name of a file to be created
            :type object_name: string
            :param picture: the FOV to be saved
            :type picture: PIL.Image.Image
        """
        file_path = path.join("Fields", "{0}.png".format(object_name))
        picture.save(file_path)

    def GetFieldsForAll(self, csv_file, dss=False):
        """
        Saves DSS or AAVSO field of view to "Fields" of the coords specified in the csv file
            :param csv_file: path to .csv file containing as follows: name of the object, ra, dec
            :type csv_file: string
            :param dss: if True, DSS field will be requested instead of AAVSO one
            :type dss: bool
        """
        with open(csv_file) as file:
            reader = csv.reader(file, skipinitialspace=True)
            next(reader, None)
            for source in reader:
                field = self.GetField(source[0], source[1], source[2], dss)
                if field is not None:
                    self.Save(source[0], field)

