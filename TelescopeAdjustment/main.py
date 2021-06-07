import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
verbose = True

test_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\3c371iS6.FIT"

path_to_reference_fields = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields"
path_to_reference_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits"
path_to_reference_catalogs = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\alipy_cats"

def make_fits(png_path):
    """
    Converts .png image to .fits one and places it to "Fields\fits"
        :param png_path: path to png image to be converted
        :type png_path: string
    """
    for im_path in glob.glob(path.join(png_path, "*.png")):
        name = path.basename(im_path)[:-4]
        im = imageio.imread(im_path)
        alipy.align.tofits("{0}\{1}.fits".format(path_to_reference_fits, name), im)

def make_cat(path):
    """
    Creates ImgCat catalog. Places it to "alipy_cats" if not presented, then loads it to memory.
    Uses SExtractor
        :param path: path to fits file
        :type path: string
    """
    cat = alipy.imgcat.ImgCat(path)
    cat.makecat(rerun=False, keepcat=True, verbose=verbose)
    cat.makestarlist(verbose=verbose)
    return cat

def make_reference_cats():
    """
    Creates ImgCat catalogs for all files in "Fields\fits" directory
    """
    ref_cats = []
    for im_path in glob.glob(path.join(path_to_reference_fits, "*.fits")):
        ref_cats.append(make_cat(im_path))
    return ref_cats

def find_transform(picture, object_name=None):
    """
    Returns Identification.trans (). The user can specify the name of reference object and the corresponding catalog will be used.
    If none, all catalogs will be viewed till one is OK.
        :param object_name: object name (ex. Q1959)
        :type object_name: string
    """
    if object_name is None:
        refs = make_reference_cats()
    else:
        cat = make_cat(path.join(path_to_reference_fits, "{0}.fits".format(object_name)))
        refs = [cat]
    obj = make_cat(picture)
    for ref_cat in refs:
        idn = alipy.ident.Identification(ref_cat, obj)
        idn.findtrans(verbose=verbose)
        if idn.ok:
            return idn.trans
        return None

#make_fits(path_to_reference_fields)
tarns = find_transform(test_fits, "3C371")

pass