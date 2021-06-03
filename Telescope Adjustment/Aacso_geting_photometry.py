import requests
import pandas as pd
import csv
from os import path
from bs4 import BeautifulSoup

URL = "https://app.aavso.org/vsp/photometry"
maglimit = '20.0'
fov = 15.0

def SendRequest(ra, dec):
    PARAMS = {'ra':ra, 'dec':dec, 'maglimit':maglimit, 'fov':fov, 'type':'photometry'}
    return requests.get(url = URL, params = PARAMS)

def GetStars(object_name, ra, dec):
    r = SendRequest(ra, dec)

    try:
        tables = pd.read_html(r.text)
    except:
        print("No comparison stars for {0}".format(object_name))
    else:
        table = tables[0]
        Save(object_name, table['AUID'], table['RA'], table['Dec'])

def Save(object_name, auid, ra, dec):
    file_path = path.join("Aavso photometry", "{0}.txt".format(object_name))
    with open(file_path, "w") as f:
        for i in range(ra.count()):
            f.write("{0}, {1}, {2}\n".format(auid[i], ra[i].split(' ')[0], dec[i].split(' ')[0]))


source_file = "test_coords.csv"
#source_file = "objects_coords.csv"

with open(source_file) as file:
    reader = csv.reader(file, skipinitialspace=True)
    next(reader, None)
    for source in reader:
        GetStars(source[0], source[1], source[2])
