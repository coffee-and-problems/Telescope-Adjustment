#! /usr/bin/env python

import glob
from os import path
import re
import fnmatch
from .camera import Camera

camera = Camera("st7_lx200")


def parse_object_file_name(fName):
    """ Function gets object name, add string (if exists) and
    filter name out of object file name"""
    # File name is like objname+addstr+filter+number.FIT,
    # for example for wcom it may be 'wcom2b001.FIT'
    fNameNoExt = path.splitext(fName)[0]
    fNameNoNumbers = fNameNoExt[:-3]
    filterCombination = fNameNoNumbers[-1]

    fNameNoFilt = fNameNoNumbers[:-1]
    # Let's find what object is it
    for line in open(path.join("references", "list_of_objects.dat")):
        objName = line.strip()
        if fNameNoFilt.startswith(objName):
            addString = fNameNoFilt[len(objName):]
            return objName, filterCombination, addString
    # No sutable object found
    return None, None, None


def get_mode(filterCombination):
    photFiltName, polarFiltName = None, None
    if filterCombination.lower() in camera.phot_filters:
            photFiltName = filterCombination
    elif filterCombination.lower() in camera.polar_filters:
            polarFiltName = filterCombination
    return photFiltName, polarFiltName


def match_files(pathToData, objName, addString, filterCombination):
    """
    Function returns list of files from the directory that look like they were
    captured with this camera
    """
    list_of_all_files = glob.glob(path.join(pathToData, "%s*" % objName))
    matched_files = []

    fileNamePattern1 = objName + addString + filterCombination + "*.fit"

    template1 = re.compile(fnmatch.translate(fileNamePattern1), re.IGNORECASE)

    for fName in list_of_all_files:
        fNameWithoutPath = path.basename(fName)
        if template1.match(fNameWithoutPath) is not None:
            matched_files.append(fName)
    return matched_files
