#! /usr/bin/env python

from math import hypot, log10, pi
import subprocess
from shutil import move
import os
from os import path
import numpy as np

try:
    import pyfits
except ImportError:
    from astropy.io import fits as pyfits


class SExCatalogue(object):
    def __init__(self, catFileName):
        self.objectList = []
        self.legend = []
        self.inds = [-1]
        self.index = 0  # For iterations
        # Parse SE catalogue with arbitrary number of objects and parameters
        for line in open(catFileName):
            sLine = line.strip()
            obj = {}
            if sLine.startswith("#"):
                # legend line
                self.legend.append(sLine.split()[2])
                self.inds.insert(-1, int(sLine.split()[1]) - 1)
                continue
            params = [float(p) for p in line.split()]
            for i in range(len(self.legend)):
                b = self.inds[i]
                e = self.inds[i+1]
                if e == b + 1:
                    obj[self.legend[i]] = params[b]
                else:
                    obj[self.legend[i]] = params[b:e]
            self.objectList.append(obj)
        self.numOfObjects = len(self.objectList)

    def find_nearest(self, x, y):
        """ Returns nearest object to given coordinates"""
        nearest = min(self.objectList, key=lambda obj: hypot(x-obj["X_IMAGE"], y-obj["Y_IMAGE"]))
        dist = hypot(x-nearest["X_IMAGE"], y-nearest["Y_IMAGE"])
        if (dist < 4.0) and (nearest["FLUX_APER"] > 0.0):
            return nearest
        else:
            return None

    def get_median_value(self, parameter):
        return np.median([obj[parameter] for obj in self.objectList])

    def get_all_values(self, parameter):
        return np.array([obj[parameter] for obj in self.objectList])

    def __iter__(self):
        return self

    def __next__(self):
        """ Iteration method """
        if self.index < self.numOfObjects:
            self.index += 1
            return self.objectList[self.index-1]
        else:
            self.index = 1
            raise StopIteration


def call_SE(fitsFile, catName=None, addString=None):
    if os.name == "nt":  # Windows OS
        pathToSex = path.join('lib', 'sex.exe')
    else:
        pathToSex = 'sex'
    pathToFile = path.join("lib", "default.sex")
    callString = " ".join([pathToSex, fitsFile, '-c %s ' % pathToFile, "-VERBOSE_TYPE QUIET"])
    if catName is not None:
        callString += " -CATALOG_NAME %s " % catName
    if addString is not None:
        callString += addString
    subprocess.call(callString, shell=True)


def find_background(addString):
    call_SE(path.join("workDir", "summed.fits"), addString=addString)
    move("background.fits", path.join("workDir", "background.fits"))
    backHDU = pyfits.open(path.join("workDir", "background.fits"))
    backData = backHDU[0].data.copy()
    backHDU.close()
    return backData


def get_photometry_phot_mode(cat, ref, filtName, aperRadius, biasValue, darkValue, backData):
    """
    This function performs photometry for a pure photometric mode.
    """
    fluxzpt = []
    stSn = {}
    for st, stObs in zip(ref.standarts, ref.standartsObs):
        if stObs["seParams"] is None:
            stSn[st['name']] = None
            continue
        # fluxAuto = stObs["seParams"]["FLUX_AUTO"]
        fluxAper1 = stObs["seParams"]["FLUX_APER"]
        xCenSt = stObs["seParams"]["X_IMAGE"]
        yCenSt = stObs["seParams"]["Y_IMAGE"]
        pValue = pi*aperRadius**2*(backData[int(yCenSt), int(xCenSt)] + darkValue + biasValue)
        snValue = fluxAper1 / (fluxAper1+pValue)**0.5
        stSn[st['name']] = snValue
        if (st["mag%s" % filtName.lower()] is not None):
            magzpt = 2.5*log10(fluxAper1) + st["mag%s" % filtName.lower()]
            fluxzpt.append(10**(0.4*(30.0-magzpt)))

    # find object magnitude and s/n ratio
    if ref.objSEParams is None:
        return None, None, None, stSn
    xCen = ref.objSEParams["X_IMAGE"]
    yCen = ref.objSEParams["Y_IMAGE"]
    objPhotParams = cat.find_nearest(xCen, yCen)
    # objFluxAuto = objPhotParams["FLUX_AUTO"]
    objFluxAper1 = objPhotParams["FLUX_APER"]
    pValue = pi*aperRadius**2*(backData[int(yCen), int(xCen)] + darkValue + biasValue)
    objSn = objFluxAper1 / (objFluxAper1+pValue)**0.5
    if st["mag%s" % filtName.lower()] is not None:
        meanZpt = 30 - 2.5*log10(np.mean(fluxzpt))
        objMag = -2.5*log10(objFluxAper1)+meanZpt
        objMagSigma = 1.0857 / objSn
    else:
        objMag = -99.0
        objMagSigma = -99.0

    return objSn, objMag, objMagSigma, stSn


def get_photometry_polar_mode(cat, ref, aperRadius, biasValue, darkValue, backData):
    """
    This function performs photometry for pure polarimetric mode. Either there is only
    one filter wheel (with polarimetric filter being in use at the moment) or there is
    two wheels but the second contains an empty slot (or a pure glass).
    """
    # we are not going to compute any magnitudes in polar mode
    # 1) find sn ratios for object pair
    fluxRatios = {}
    if ref.objSEParams is not None:
        xObjCen = ref.objSEParams["X_IMAGE"]
        yObjCen = ref.objSEParams["Y_IMAGE"]
        objPhotParams = cat.find_nearest(xObjCen, yObjCen)
        # objFluxAuto = objPhotParams["FLUX_AUTO"]
        objFluxAper1 = objPhotParams["FLUX_APER"]
        pValue = pi*aperRadius**2*(backData[int(yObjCen), int(xObjCen)] + darkValue + biasValue)
        objSN = objFluxAper1 / (objFluxAper1+pValue)**0.5

    else:
        objSN = None
        objFluxAper1 = None
    # pair
    if ref.objPairSEParams is not None:
        xObjPairCen = ref.objPairSEParams["X_IMAGE"]
        yObjPairCen = ref.objPairSEParams["Y_IMAGE"]
        objPairPhotParams = cat.find_nearest(xObjPairCen, yObjPairCen)
        # objPairFluxAuto = objPairPhotParams["FLUX_AUTO"]
        objPairFluxAper1 = objPairPhotParams["FLUX_APER"]
        pValue = pi*aperRadius**2*(backData[int(yObjPairCen), int(xObjPairCen)] + darkValue + biasValue)
        objPairSN = objPairFluxAper1 / (objPairFluxAper1+pValue)**0.5

    else:
        objPairSN = None
        objPairFluxAper1 = None
    if (objFluxAper1 is not None) and (objPairFluxAper1 is not None):
        fluxRatios["obj"] = objFluxAper1 / objPairFluxAper1
    else:
        fluxRatios["obj"] = None
    # 2) find sn ratios for standart pairs
    stSnDict = {}
    stFluxRatios = []
    for st, stPair in zip(ref.standartsObs, ref.standartPairsObs):
        if not st["seParams"] is None:
            # stFluxAuto = st["seParams"]["FLUX_AUTO"]
            stFluxAper1 = st["seParams"]["FLUX_APER"]
            xCenSt = st["seParams"]["X_IMAGE"]
            yCenSt = st["seParams"]["Y_IMAGE"]
            pValue = pi*aperRadius**2*(backData[int(yCenSt), int(xCenSt)] + darkValue + biasValue)
            stSN = stFluxAper1/(stFluxAper1+pValue)**0.5
        else:
            stSN = None
            stFluxAper1 = None
        if not stPair["seParams"] is None:
            # stPairFluxAuto = stPair["seParams"]["FLUX_AUTO"]
            stPairFluxAper1 = stPair["seParams"]["FLUX_APER"]
            xCenSt = stPair["seParams"]["X_IMAGE"]
            yCenSt = stPair["seParams"]["Y_IMAGE"]
            pValue = pi*aperRadius**2*(backData[int(yCenSt), int(xCenSt)] + darkValue + biasValue)
            stPairSN = stPairFluxAper1/(stPairFluxAper1+pValue)**0.5
        else:
            stPairSN = None
            stPairFluxAper1 = None
        stSnDict[st["name"]] = np.array([stSN, stPairSN])
        if (stFluxAper1 is not None) and (stPairFluxAper1 is not None):
            stFluxRatios.append(stFluxAper1/stPairFluxAper1)
    if stFluxRatios:
        fluxRatios["st"] = np.mean(stFluxRatios)
    else:
        fluxRatios["st"] = None
    return objSN, objPairSN, stSnDict, fluxRatios


def get_photometry_mixed_mode(cat, ref, photFiltName, aperRadius, biasValue, darkValue, backData):
    """
    This function performs photometry for a mixed photometric+polarimetric mode
    """
    fluxzpt = []
    stSn = {}
    # Find magnitude zeropoint
    for st, stObs, stPairObs in zip(ref.standarts, ref.standartsObs, ref.standartPairsObs):
        if (stObs["seParams"] is None) or (stPairObs["seParams"] is None):
            stSn[st['name']] = None
            continue
        fluxAper = stObs["seParams"]["FLUX_APER"]
        fluxAperPair = stPairObs["seParams"]["FLUX_APER"]
        fluxAperCombined = fluxAper + fluxAperPair  # Total flux of polarimetric pair
        xCenSt = stObs["seParams"]["X_IMAGE"]
        yCenSt = stObs["seParams"]["Y_IMAGE"]
        xCenStPair = stPairObs["seParams"]["X_IMAGE"]
        yCenStPair = stPairObs["seParams"]["Y_IMAGE"]
        # Combined noise value
        pValue = pi*aperRadius**2*(backData[int(yCenSt), int(xCenSt)] + darkValue + biasValue)
        pValue += pi*aperRadius**2*(backData[int(yCenStPair), int(xCenStPair)] + darkValue + biasValue)
        snValue = fluxAperCombined / (fluxAperCombined+pValue) ** 0.5
        stSn[st['name']] = snValue
        if (st["mag%s" % photFiltName.lower()] is not None):
            magzpt = 2.5*log10(fluxAperCombined) + st["mag%s" % photFiltName.lower()]
            fluxzpt.append(10**(0.4*(30.0-magzpt)))

    # Find object magnitude and s/n ratio
    if (ref.objSEParams is None) or (ref.objPairSEParams is None):
        return None, None, None, stSn
    xCen = ref.objSEParams["X_IMAGE"]
    yCen = ref.objSEParams["Y_IMAGE"]
    objPhotParams = cat.find_nearest(xCen, yCen)
    objFluxAper = objPhotParams["FLUX_APER"]
    xCenPair = ref.objPairSEParams["X_IMAGE"]
    yCenPair = ref.objPairSEParams["Y_IMAGE"]
    objPairPhotParams = cat.find_nearest(xCenPair, yCenPair)
    objPairFluxAper = objPairPhotParams["FLUX_APER"]
    objFluxAperCombined = objFluxAper + objPairFluxAper  # Total signal of the object pair
    pValue = pi*aperRadius**2*(backData[int(yCen), int(xCen)] + darkValue + biasValue**2.0)
    pValue += pi*aperRadius**2*(backData[int(yCenPair), int(xCenPair)] + darkValue + biasValue**2.0)
    objSn = objFluxAperCombined / (objFluxAperCombined+pValue)**0.5
    if st["mag%s" % photFiltName.lower()] is not None:
        meanZpt = 30 - 2.5*log10(np.mean(fluxzpt))
        objMag = -2.5*log10(objFluxAperCombined)+meanZpt
        objMagSigma = 1.0857 / objSn
    else:
        objMag = -99.0
        objMagSigma = -99.0
    return objSn, objMag, objMagSigma, stSn


def all_st_sn_decreased(stSnOld, stSnNew, polarMode):
    if polarMode:
        for key in stSnOld:
            if (key in stSnNew):
                a1 = stSnOld[key]
                sOld = sum(a1[np.where(a1 != np.array(None))])
                a2 = stSnNew[key]
                sNew = sum(a2[np.where(a2 != np.array(None))])
                if (sOld < sNew):
                    return False
    else:
        for key in stSnOld:
            if (key in stSnNew):
                sOld = stSnOld[key]
                sNew = stSnNew[key]
                if (sOld is not None) and (sNew is not None) and (sOld < sNew):
                    return False
    return True