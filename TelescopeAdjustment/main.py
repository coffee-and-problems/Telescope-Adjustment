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
obj = "s50716iS6"
ref = "s50716"
ra = '07 21 53.4'
dec = '71 20 36'

#Geting Gaia catalogs
gaia = Gaia_data()
gaia.make_ref_cat(ref, ra, dec, fov)


#Finding transform for the field observed
adj = Adjustment(verbose=True, keepcat=True)
observed_field = r"observations\{0}.FIT".format(obj)

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
