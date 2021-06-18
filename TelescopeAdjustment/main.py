import numpy as np
import imageio
import glob
from os import path

from lib import alipylocal as alipy
from Aavso import Aavso
from Gaia import Gaia
from Adjustment import Adjustment

import matplotlib.pyplot as plt
from astropy.io import fits
plt.figure(figsize=(6.00, 6.00), dpi=100)
plt.axis('equal')

#obj = "q1959iS4"
#ref = "q1959"
#ra = '19 59 59.8'
#dec = '65 08 54'
obj = "s50716iS6"
ref = "s50716"
ra = '07 21 53.4'
dec = '71 20 36'

#Geting Gaia catalogs
gaia = Gaia()
coords = gaia.coords_to_deg(ra, dec)
(x,y) = gaia.get_box(coords, 10, 5) 

s1 = gaia.parse_gaia_results("{0}.gz".format(ref))
#s2 = gaia.map(s1, , 528, gaia.coords_to_deg('19 59 59.8', '65 08 54'))
s2 = gaia.map(s1, 10, 528, coords)
gaia.save_sex_cat(f"{ref}alipysexcat", s2)


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
