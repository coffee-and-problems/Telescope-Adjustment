import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
verbose = False

test_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits\OC457.fits"

path_to_reference_fields = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields"
path_to_reference_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits"
path_to_reference_catalogs = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\alipy_cats"

def make_fits(png_path):
    for im_path in glob.glob(path.join(png_path, "*.png")):
        name = path.basename(im_path)[:-4]
        im = imageio.imread(im_path)
        alipy.align.tofits("{0}\{1}.fits".format(path_to_reference_fits, name), im)

def make_cat(path):
    cat = alipy.imgcat.ImgCat(path)
    cat.makecat(rerun=False, keepcat=True, verbose=verbose)
    cat.makestarlist(verbose=verbose)
    return cat

def make_reference_cats():
    ref_cats = []
    for im_path in glob.glob(path.join(path_to_reference_fits, "*.fits")):
        ref_cats.append(make_cat(im_path))
    return ref_cats

def find_transform(picture, object_name=None):
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

#make_fits(path_to_reference_fields)
tarns = find_transform(test_fits)
