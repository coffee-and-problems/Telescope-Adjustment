from PIL import Image, ImageOps
import numpy as np
import imageio
import glob
from os import path
from astropy.table import Table

from lib import alipylocal as alipy

test_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\q1959iS4.FIT"

#(pixelarray, hdr) = alipy.align.fromfits(test_fits)
#pixelarray = np.log(pixelarray).astype(int)
#img = Image.fromarray(pixelarray)
##img = img.convert('L')
##inverted_image = ImageOps.invert(img)
##inverted_image = inverted_image.convert('1')
##img.save('q1959iS4.png')
#img.show()

fits_table = r"axy.fits"
t = Table.read(fits_table)
x = t['X']
y = t['Y']
flux = t['FLUX']

file_path = path.join("alipy_cats", "site.txt")
with open(file_path, 'w') as file:
    file.write("#   1 NUMBER          Running object number\n")
    file.write("#   2 X_IMAGE         Object position along x                         [pixel]\n")
    file.write("#   3 Y_IMAGE         Object position along y                         [pixel]\n")
    file.write("#   4 FLUX_AUTO       Flux within a Kron-like elliptical aperture     [count]\n")
    file.write("#   5 FWHM_IMAGE      FWHM assuming a gaussian core                   [pixel]\n")
    file.write("#   6 FLAGS           Extraction flags\n")
    file.write("#   7 ELONGATION      A_IMAGE/B_IMAGE\n")

    for i in range(len(x)):
        X = x[i]
        Y = y[i]
        f = flux[i]
        #file.write(f'{i+1:{10}}{star.ra:{11}}{star.dec:{11}}{star.flux:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')
        file.write(f'{i+1:{10}}{X:{11}.{5}}{Y:{11}.{5}}{f:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')



pass