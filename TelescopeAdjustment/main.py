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
observed_field = r"C:\Users\maryc\source\repos\TelescopeAdjustment\TelescopeAdjustment\observations\ds9.fits"
tarns = adj.find_transform(observed_field, "q1959iS5")
