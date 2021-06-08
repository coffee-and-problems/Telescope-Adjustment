from PIL import Image, ImageOps
import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy

test_fits = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\q1959iS4.FIT"

(pixelarray, hdr) = alipy.align.fromfits(test_fits)
pixelarray = np.log(pixelarray).astype(int)
img = Image.fromarray(pixelarray)
#img = img.convert('L')
#inverted_image = ImageOps.invert(img)
#inverted_image = inverted_image.convert('1')
#img.save('q1959iS4.png')
img.show()
