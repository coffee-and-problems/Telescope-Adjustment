#! /usr/bin/env python

"""
Definitions related to cameras and their parameters
"""

from os import path
from glob import glob


path_to_cameras = path.dirname(__file__)
list_of_cameras = [path.basename(path.splitext(f)[0]) for f in glob(path.join(path_to_cameras, "*.params"))]


class Camera(object):
    def __init__(self, name):
        # Parse file with parameters
        cameraFile = path.join(path_to_cameras, "%s.params" % name)
        self.polar_pair_shift = [[], []]
        for line in open(cameraFile):
            if line.startswith("resolution_x"):
                self.resolution_x = float(line.split()[1])
                continue
            if line.startswith("resolution_y"):
                self.resolution_y = float(line.split()[1])
                continue
            if line.startswith("phot_filters"):
                self.phot_filters = [c.lower() for c in line.split()[1].split(",")]
                continue
            if line.startswith("polar_filters"):
                self.polar_filters = [c.lower() for c in line.split()[1].split(",")]
                continue
            if line.startswith("two_wheels"):
                if line.split()[1] == "True":
                    self.two_wheels = True
                else:
                    self.two_wheels = False
            if line.startswith("polar_pair_shift_first"):
                dx = float(line.split()[1].split(",")[0])
                dy = float(line.split()[1].split(",")[1])
                self.polar_pair_shift[0] = (dx, dy)
                continue
            if line.startswith("polar_pair_shift_second"):
                dx = float(line.split()[1].split(",")[0])
                dy = float(line.split()[1].split(",")[1])
                self.polar_pair_shift[1] = (dx, dy)
                continue
            if line.startswith("darks_required"):
                self.darks_required = int(line.split()[1])
                continue
            if line.startswith("biases_required"):
                self.biases_required = int(line.split()[1])
                continue

            if line.startswith("flip_flat_ud"):
                if line.split()[1] == "True":
                    self.flip_flat_ud = True
                else:
                    self.flip_flat_ud = False

            if line.startswith("flip_flat_lr"):
                if line.split()[1] == "True":
                    self.flip_flat_lr = True
                else:
                    self.flip_flat_lr = False

            if line.startswith("flip_data_ud"):
                if line.split()[1] == "True":
                    self.flip_data_ud = True
                else:
                    self.flip_data_ud = False

            if line.startswith("flip_data_lr"):
                if line.split()[1] == "True":
                    self.flip_data_lr = True
                else:
                    self.flip_data_lr = False
