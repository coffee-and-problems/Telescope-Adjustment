#Trash module, don't look here
#from PIL import Image, ImageOps
#import numpy as np
#import imageio
#import glob
#from os import path
#from astropy.table import Table

#from lib import alipylocal as alipy

#import matplotlib.pyplot as plt
#plt.figure(figsize=(6.00, 6.00), dpi=100)
#plt.axis('equal')

#file = r"viz.csv"
#x, y = np.genfromtxt(file, delimiter=",", usecols=(1, 2), unpack=True)
#plt.plot(x, y, "rx")
#plt.show()

#Plotting data
#import matplotlib.pyplot as plt

#plt.figure(figsize=(6.00, 6.00), dpi=100)
#plt.axis('equal')
#x, y = np.genfromtxt(r"alipy_cats\{0}alipysexcat".format(ref), usecols=(1, 2), unpack=True)
#data = fits.getdata(observed_field)
#plt.imshow(data, origin="lower", vmin=1700, vmax=3000)
#plt.plot(x, y, "rx")
#plt.show()

#trans = trans.inverse()
#stars = adj.get_stars(ref)
#stars3 = trans.applystarlist(stars)

#x_trans = []
#y_trans = []
#for star in stars3:
#    x_trans.append(star.x)
#    y_trans.append(star.y)


#plt.imshow(data, origin="lower", vmin=1700, vmax=3000)
#plt.plot(x_trans, y_trans, "rx")
#plt.show()

from statistics import median
import os

def find_median(file):
    with open(file) as f:
        name = os.path.basename(f.name)[:-4]
        RA = []
        DEC = []
        for line in f:
            sl = line.split()
            RA.append(float(sl[0]))
            DEC.append(float(sl[1]))
        ra = median(RA)
        dec = median(DEC)
    return (name, ra, dec)


with open("result_file.txt", 'w') as result_file:
    for root, dirs, files in os.walk("results", topdown=False):
       for file in files:
          obj = find_median(os.path.join(root, file))
          result_file.write(f"{obj[0]} {obj[1]} {obj[2]}\n")

pass