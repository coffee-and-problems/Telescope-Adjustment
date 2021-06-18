from PIL import Image, ImageOps
import numpy as np
import imageio
import glob
from os import path
from astropy.table import Table

from lib import alipylocal as alipy

import matplotlib.pyplot as plt
plt.figure(figsize=(6.00, 6.00), dpi=100)
plt.axis('equal')

file = r"viz.csv"
x, y = np.genfromtxt(file, delimiter=",", usecols=(1, 2), unpack=True)
plt.plot(x, y, "rx")
plt.show()



pass