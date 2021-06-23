import numpy as np
import imageio
import glob
import csv
from os import path

from lib import alipylocal as alipy
from Gaia import Gaia_data
from Adjustment import Adjustment

from astropy.io import fits


class Main():
    """Main class"""
    def __init__(self, object_name, observation, source_file):
        """
            :param object_name: object name
            :type object_name: string
            :param observation: path to .FIT file containing the observation
            :type observation: string
            :param source_file: path to.txt file containing as follows: name of the object, ra, dec
            :type source_file: string
        """
        self.fov = 10
        self.observation = observation
        self.ref = object_name
        with open(source_file) as file:
            for line in file:
                source = line.split()
                s = " "
                if (source[0] == self.ref):
                    self.ra = s.join([source[1], source[2], source[3]])
                    self.dec = s.join([source[4], source[5], source[6]])

    def run(self):
        """
        Returns the center of the observed image in deg
        """
        #Geting Gaia catalogs
        gaia = Gaia_data()
        adj = Adjustment(verbose=False, keepcat=True)

        #We will download the data only if the desired catalog is not present
        if not path.isfile(path.join(adj.path_to_reference_catalogs, f"{self.ref}alipysexcat")):
            gaia.make_ref_cat(self.ref, self.ra, self.dec, self.fov)

        #Finding transform for the field observed
        trans = adj.find_transform(self.observation, self.ref)

        #Obtaining telescope adjustment in arcsecs
        shift = trans.get_shift()

        coords = gaia.coords_to_deg(self.ra, self.dec)
        ratio_x, ratio_y = gaia.get_ratio(self.fov, coords)
        ratio_x_arcsec = ratio_x / 3600
        ratio_y_arcsec = ratio_y / 3600
        print("x, y offset, pxl: {0}".format(shift))
        shift_ra = shift[0]/ratio_x_arcsec
        shift_dec = shift[1]/ratio_y_arcsec
        print("ra, dec offset, arcsec: {0}, {1}".format(shift_ra, shift_dec))
        return (coords[0] + shift[0]/ratio_x, coords[1] + shift[1]/ratio_y)

#Usage example
#main = Main("q1959", "observations\q1959iS4.FIT", "TABOB.txt")
#a = main.run()
#print(a)
