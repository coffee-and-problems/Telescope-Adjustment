import os
from os import path
import numpy as np
import scipy.ndimage
try:
        import pyfits
except ImportError:
        from astropy.io import fits as pyfits


def affineremap(filepath, transform, shape, alifilepath=None, outdir="alipy_out", hdu=0, verbose=False):
    """
    Apply the simple affine transform to the image and saves the result as FITS, without using pyraf.

    :param filepath: FITS file to align
    :type filepath: string

    :param transform: as returned e.g. by alipy.ident()
    :type transform: SimpleTransform object

    :param shape: Output shape (width, height)
    :type shape: tuple

    :param alifilepath: where to save the aligned image. If None, I will put it in the outdir directory.
    :type alifilepath: string

    :param hdu: The hdu of the fits file that you want me to use. 0 is primary. If multihdu, 1 is usually science.

    """
    inv = transform.inverse()
    (matrix, offset) = inv.matrixform()

    data, hdr = fromfits(filepath, hdu=hdu, verbose=verbose)
    data = scipy.ndimage.interpolation.affine_transform(data, matrix, offset=offset, output_shape=shape)

    basename = path.splitext(path.basename(filepath))[0]

    if alifilepath is None:
        alifilepath = path.join(outdir, basename + "_affineremap.fits")
    else:
        outdir = path.split(alifilepath)[0]
    if not path.isdir(outdir):
        os.makedirs(outdir)

    tofits(alifilepath, data, verbose=verbose)


def shape(filepath, hdu=0, verbose=False):
    """
    Returns the 2D shape (width, height) of a FITS image.

    :param hdu: The hdu of the fits file that you want me to use. 0 is primary. If multihdu, 1 is usually science.

    """
    hdr = pyfits.getheader(filepath, hdu)
    if hdr["NAXIS"] != 2:
        raise RuntimeError("Hmm, this hdu is not a 2D image!")
    if verbose:
        print("Image shape of %s : (%i, %i)" % (path.basename(filepath), int(hdr["NAXIS1"]), int(hdr["NAXIS2"])))
    return (int(hdr["NAXIS1"]), int(hdr["NAXIS2"]))


def fromfits(infilename, hdu=0):
    """
    Reads a FITS file and returns a 2D numpy array of the data.
    Use hdu to specify which HDU you want (default = primary = 0)
    """
    pixelarray, hdr = pyfits.getdata(infilename, hdu, header=True)
    pixelarray = np.asarray(pixelarray).transpose()
    return pixelarray, hdr


def tofits(outfilename, pixelarray):
    """
    Takes a 2D numpy array and write it into a FITS file.
    If you specify a header (pyfits format, as returned by fromfits()) it will be used for the image.
    You can give me boolean numpy arrays, I will convert them into 8 bit integers.
    """
    if pixelarray.dtype.name == "bool":
        pixelarray = np.cast["uint8"](pixelarray)

    pyfits.PrimaryHDU(pixelarray.transpose()).writeto(outfilename, overwrite=True)
