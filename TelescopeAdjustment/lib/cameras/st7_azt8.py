#! /usr/bin/env python

import glob
from os import path
import re
import fnmatch
from .camera import Camera

camera = Camera("st7_azt8")


def parse_object_file_name(fName):
    """ Function gets object name, add string (if exists) and
    filter name out of object file name"""
    # File name is like objname+[addstr]+filter[s]+number.FIT,
    # for example for wcom it may be 'cicam1Qr001.FIT'
    fNameNoExt = path.splitext(fName)[0]

    # Let's find what object is it
    for line in open(path.join("references", "list_of_objects.dat")):
        objName = line.strip()
        if fNameNoExt.startswith(objName):
            break
    else:
        # No sutable object found
        return None, None, None

    # Find addstring. It has to be numerical and has to be followed by a
    # filter (i.e. non-numerical)
    addString = ''
    for i, c in enumerate(fNameNoExt[len(objName):]):
        if c.isnumeric():
            addString += c
        else:
            addStringEndIdx = i - 1
            break
    # Find filter
    filterAndFrameNumber = fNameNoExt[len(objName) + addStringEndIdx + 1:]

    # Now we have only filter and frame number in our string. It looks like Qr012 now.
    # filter combination
    filterCombination = filterAndFrameNumber[:-3]

    # That's it. Return all values now and hope for the best...
    return objName, filterCombination, addString


def get_mode(filterCombination):
    photFiltName, polarFiltName = None, None
    for c in filterCombination:
        if c.lower() in camera.phot_filters:
            photFiltName = c
        elif c.lower() in camera.polar_filters:
            polarFiltName = c
    return photFiltName, polarFiltName


def match_files(pathToData, objName, addString, filterCombination):
    """
    Function returns list of files from the directory that look like they were
    captured with this camera
    """
    list_of_all_files = glob.glob(path.join(pathToData, "%s*" % objName))
    matched_files = []

    # To take into account the possibility that user can accidentally switch the order of filters
    # in the file name (e.g. bllacrx instead of bllacxr) we will perform the searching twice
    fileNamePattern1 = objName + addString + filterCombination + "*.fit"
    fileNamePattern2 = objName + addString + filterCombination[-1::-1] + "*.fit"

    template1 = re.compile(fnmatch.translate(fileNamePattern1), re.IGNORECASE)
    template2 = re.compile(fnmatch.translate(fileNamePattern2), re.IGNORECASE)

    for fName in list_of_all_files:
        fNameWithoutPath = path.basename(fName)
        if (template1.match(fNameWithoutPath) is not None) or (template2.match(fNameWithoutPath) is not None):
            matched_files.append(fName)
    return matched_files
