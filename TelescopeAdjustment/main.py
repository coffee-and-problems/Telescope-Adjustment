import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
verbose = True

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

def make_reference_cats(path_to_reference_fits):
    ref_cats = []
    for im_path in glob.glob(path.join(path_to_reference_fits, "*.fits")):
        ref_cats.append(make_cat(im_path))

def find_reference(picture):
    refs = []
    obj = make_cat(picture)
    #for ref_cat in glob.glob(path.join(path_to_reference_catalogs, "*")):
    for ref_cat in ref_cats:
        idn = alipy.ident.Identification(ref_cat, obj)
        print("aha")
        idn.findtrans(verbose=verbose)
        refs.append(idn)
    return refs

#make_fits(path_to_reference_fields)
#make_reference_cats(path_to_reference_fits)
refs = find_reference(test_fits)
