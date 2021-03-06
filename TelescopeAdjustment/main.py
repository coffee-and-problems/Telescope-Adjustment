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
    def __init__(self, object_name, observation, source_file, fov, matrix_pixels):
        """
            :param object_name: object name
            :type object_name: string
            :param observation: path to .FIT file containing the observation
            :type observation: string
            :param source_file: path to.txt file containing as follows: name of the object, ra, dec
            :type source_file: string
        """
        self.fov = fov
        self.matrix_pixels = matrix_pixels
        self.observation = observation
        self.ref = object_name
        with open(source_file) as file:
            for line in file:
                source = line.split()
                s = " "
                if (source[0] == self.ref):
                    self.ra = float(source[1])
                    self.dec = float(source[2])

    def run(self):
        """
        Returns the center of the observed image in deg
        """
        #Geting Gaia catalogs
        gaia = Gaia_data(self.fov, self.matrix_pixels)
        adj = Adjustment(verbose=False, keepcat=True)

        #We will download the data only if the desired catalog is not present
        if not path.isfile(path.join(adj.path_to_reference_catalogs, f"{self.ref}alipysexcat")):
            gaia.make_ref_cat(self.ref, self.ra, self.dec)

        #Finding transform for the field observed
        trans = adj.find_transform(self.observation, self.ref)

        #Obtaining telescope adjustment in arcsecs
        shift = trans.get_shift()

        coords = (self.ra, self.dec)
        ratio = self.fov * 60 / self.matrix_pixels
        print("x, y offset, pxl: {0}".format(shift))
        shift_ra = shift[0] * ratio
        shift_dec = shift[1] * ratio
        print("ra, dec offset, arcsec: {0}, {1}".format(shift_ra, shift_dec))
        return (shift_ra, shift_dec)

#Usage example
main = Main("q1959", "observations\q1959iS4.FIT", "objects_coords.txt", 10, 528)
a = main.run()
print(a)
