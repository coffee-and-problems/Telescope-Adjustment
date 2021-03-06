import numpy as np
import imageio
import glob
import csv
from os import path

from lib import alipylocal as alipy
from Gaia import Gaia_data
from Adjustment import Adjustment

from astropy.io import fits

class TelescopeAdjastment():
    """Public interface for TelescopeAdjastment sublibrary"""

    def __init__(self, object_name, observation, source_file):
        """
            :param object_name: object name
            :type object_name: string
            :param observation: path to .FIT file containing the observation
            :type observation: string
            :param source_file: path to .csv file containing as follows: name of the object, ra, dec
            :type source_file: string
        """
        self.fov = 10
        self.observation = observation
        self.ref = object_name
        with open(source_file) as file:
            reader = csv.reader(file, skipinitialspace=True)
            next(reader, None)
            for source in reader:
                if (source[0] == self.ref):
                    self.ra = source[1]
                    self.dec = source[2]

    def run(self):
        """
        Returns (dx, dy) in arcsecs
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
        return (shift_ra, shift_dec)