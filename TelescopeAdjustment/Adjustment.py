import numpy as np
import imageio
import glob
from os import path
from PIL import Image

from lib import alipylocal as alipy

class Adjustment(object):
    """Class to find transform between an observation and reference object(s)"""

    def __init__(self, verbose=False, keepcat=True):
        self.verbose = verbose
        self.keepcat = keepcat
        self.path_to_reference_fields = "Fields"
        self.path_to_reference_fits = path.join(self.path_to_reference_fields, "fits")
        self.path_to_reference_catalogs = "alipy_cats"

    def make_fits(self, png_path):
        """
        Converts .png image to .fits one and places it to "Fields\fits"
            :param png_path: path to png image to be converted
            :type png_path: string
        """
        for im_path in glob.glob(path.join(png_path, "*.png")):
            name = path.basename(im_path)[:-4]
            im = Image.open(im_path).convert('L')
            im_array = np.array(im)
            im_array = np.rot90(im_array, 3)
            fits_path = path.join(self.path_to_reference_fits, "{0}.fits".format(name))
            alipy.align.tofits(fits_path, im_array)

    def make_cat(self, path, keepcat=True):
        """
        Creates ImgCat catalog. Places it to "alipy_cats" if not presented, then loads it to memory.
        Uses SExtractor
            :param path: path to fits file
            :type path: string
        """
        cat = alipy.imgcat.ImgCat(path)
        cat.makecat(rerun=False, keepcat=self.keepcat, verbose=self.verbose)
        cat.makestarlist(verbose=self.verbose)
        return cat

    def get_stars(self, path):
        cat = self.make_cat(path)
        return cat.starlist

    def make_reference_cats(self):
        """
        Creates ImgCat catalogs for all files in "Fields\fits" directory
        """
        ref_cats = []
        for im_path in glob.glob(path.join(self.path_to_reference_fits, "*.fits")):
            ref_cats.append(self.make_cat(im_path))
        return ref_cats

    def find_transform(self, picture, object_name=None):
        """
        Returns Identification.trans (). The user can specify the name of reference object and the corresponding catalog will be used.
        If none, all catalogs will be viewed till one is OK.
            :param object_name: object name (ex. Q1959)
            :type object_name: string
        """
        if object_name is None:
            refs = self.make_reference_cats()
        else:
            cat = self.make_cat(path.join(self.path_to_reference_fits, "{0}.fits".format(object_name)))
            refs = [cat]
        obj = self.make_cat(picture)
        for ref_cat in refs:
            idn = alipy.ident.Identification(ref_cat, obj)
            idn.findtrans(verbose=self.verbose)
            if idn.ok:
                return idn.trans
            return None

    def clear(self, mode):
        """
        Deletes cats, reference fits or all of it.
            :param mode: "cats" for deleting only cats, "fits" for reference fits or "all" for all
            :type object_name: string
        """
        from os import remove

        if mode == "cats":
            for cat in glob.glob(path.join(self.path_to_reference_catalogs, "*")):
                remove(cat)
        elif mode == "fits":
            for fits in glob.glob(path.join(self.path_to_reference_fits, "*.fits")):
                remove(fits)
        elif mode == "all":
            self.clear("cats")
            self.clear("fits")
        else:
            print("Unknown mode! What should I delete?")
