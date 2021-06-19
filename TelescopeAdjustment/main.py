import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
from Gaia import Gaia_data
from Adjustment import Adjustment

import matplotlib.pyplot as plt
from astropy.io import fits
plt.figure(figsize=(6.00, 6.00), dpi=100)
plt.axis('equal')

fov = 10
observation = "s50716iS6"
ref = "s50716"

#Geting Gaia catalogs
source_file = "test_coords.csv"
#source_file = "objects_coords.csv

gaia = Gaia_data()
gaia.make_ref_cats_for_all(source_file)


#Finding transform for the field observed
adj = Adjustment(verbose=True, keepcat=True)
observed_field = r"observations\{0}.FIT".format(observation)

x, y = np.genfromtxt(r"alipy_cats\{0}alipysexcat".format(ref), usecols=(1, 2), unpack=True)
data = fits.getdata(observed_field)
#plt.imshow(data, origin="lower", vmin=1700, vmax=3000)
plt.plot(x, y, "rx")
plt.show()

trans = adj.find_transform(observed_field, ref)
trans = trans.inverse()
stars = adj.get_stars(ref)
stars3 = trans.applystarlist(stars)

x_trans = []
y_trans = []
for star in stars3:
    x_trans.append(star.x)
    y_trans.append(star.y)


plt.imshow(data, origin="lower", vmin=1700, vmax=3000)
plt.plot(x_trans, y_trans, "rx")
plt.show()
