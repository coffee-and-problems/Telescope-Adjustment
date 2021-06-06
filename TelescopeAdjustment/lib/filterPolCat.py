#! /usr/bin/env python


from math import hypot
import numpy as np


def filterPolCat(catInName, catOutName, polarFilterName, camera):
    matchDist = 3.0
    polarFilterName = polarFilterName.lower()
    polarFilterIdx = camera.polar_filters.index(polarFilterName)
    shift_dx = camera.polar_pair_shift[polarFilterIdx][0]
    shift_dy = camera.polar_pair_shift[polarFilterIdx][1]

    cat = np.genfromtxt(catInName)
    # Sort catalogue by x-coordinate
    try:
        cat = cat[np.argsort(cat[:, 1])]
    except IndexError:
        # empty cat
        return None
    pairs = []

    for i, obj in enumerate(cat):
        xObj = obj[1]
        yObj = obj[2]
        xPair = xObj + shift_dx
        yPair = yObj + shift_dy
        minDist = 1e5

        for obj2 in cat[i:]:
            x2 = obj2[1]
            y2 = obj2[2]
            if x2 > xPair + 10:
                # Pair object can not be so far away from the original one
                break
            dist = hypot(x2-xPair, y2-yPair)
            if dist < minDist:
                minDist = dist
                pairObj = obj2
        if minDist < matchDist:
            # possible pair object found
            pairs.append((obj, pairObj))

    fout = open(catOutName, "w")
    fout.truncate(0)
    for line in open(catInName):
        if line.startswith("#"):
            fout.write(line)
    for objNum, pair in enumerate(pairs):
        outStr = " ".join([str(v) for v in pair[0][1:]])
        fout.write("%i %s\n" % (objNum+1, outStr))
    fout.close()


# filterPolCat("field.cat", "out.cat", "x")
