import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
from Aavso import Aavso
from Adjustment import Adjustment

##Downloading reference pictures
#source_file = "test_coords.csv"
##source_file = "objects_coords.csv
#aavso = Aavso()
#aavso.GetFieldsForAll(source_file, dss=True)

#Wrapping reference images in .fits
adj = Adjustment(True)
#adj.make_fits("Fields")

#Finding transform for the field observed
observed_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\q1959iS4.FIT"
ref_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits\Q1959.fits"

stars1 = adj.get_stars(observed_field)
stars2 = adj.get_stars(ref_field)

import matplotlib.pyplot as plt
from astropy.io import fits
data = plt.imread(r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\Q1959.png")

x=[]
y=[]
for star in stars2:
    x.append(star.x)
    y.append(star.y)

#for star in stars2:
#    x.append(star.x)
#    y.append(star.y)

data = fits.getdata(r"Fields\fits\Q1959.fits")
plt.imshow(data, origin="lower", vmin=10, vmax=255)
plt.plot(x, y, "rx")
plt.show()
#tarns = adj.find_transform(observed_field, "Q1959")

#adj.clear("cats")