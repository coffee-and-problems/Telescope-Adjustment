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
adj = Adjustment(verbose=True, keepcat=True)
#adj.clear("all")
#adj.make_fits("Fields")

#Finding transform for the field observed
observed_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\q1959iS4.FIT"
#observed_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits\Q1959dss.fits"
ref_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\Fields\fits\Q1959.fits"

stars1 = adj.get_stars(observed_field)
stars2 = adj.get_stars(ref_field)

import matplotlib.pyplot as plt
from astropy.io import fits
plt.figure(figsize=(5.00, 6.00), dpi=100)

#x1=[]
#y1=[]
#for star in stars1:
#    x1.append(star.x)
#    y1.append(star.y)

#x2=[]
#y2=[]
#for star in stars2:
#    x2.append(star.x)
#    y2.append(star.y)

#data = fits.getdata(r"observations\q1959iS4.FIT")
#plt.imshow(data, origin="lower", vmin=1700, vmax=3000)
#plt.plot(x1, y1, "yx")
#plt.show()

#data = fits.getdata(r"Fields\fits\Q1959.fits")
#plt.imshow(data, origin="lower", vmin=10, vmax=255)
#plt.plot(x2, y2, "rx")
#plt.show()

x, y = np.genfromtxt("alipy_cats\Q1959alipysexcat", usecols=(1, 2), unpack=True)
#x, y = np.genfromtxt("alipy_cats\s1", usecols=(1, 2), unpack=True)
plt.plot(x, y, "y.")
plt.show()
tarns = adj.find_transform(observed_field, "Q1959")
