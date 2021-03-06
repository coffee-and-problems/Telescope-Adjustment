from . import imgcat
from . import quad
from . import star


class Identification:
    """
    Represents the identification of a transform between two ImgCat objects.
    Regroups all the star catalogs, the transform, the quads, the candidate, etc.

    All instance attributes are listed below.

    :ivar ref: ImgCat object of the reference image
    :ivar ukn: ImgCat object of the unknown image
    :ivar ok: boolean, True if the idendification was successful.
    :ivar trans: The SimpleTransform object that represents the geometrical transform from ukn to ref.
    :ivar uknmatchstars: A list of Star objects of the catalog of the unknown image...
    :ivar refmatchstars: ... that correspond to these Star objects of the reference image.
    """

    def __init__(self, ref, ukn):
        """
        :param ref: The reference image
        :type ref: ImgCat object
        :param ukn: The unknown image, whose transform will be adjusted to match the ref
        :type ukn: ImgCat object
        """
        self.ref = ref
        self.ukn = ukn

        self.ok = False

        self.trans = None
        self.uknmatchstars = []
        self.refmatchstars = []
        self.cand = None

    def findtrans(self, r=5.0, verbose=False):
        """
        Find the best trans given the quads, and tests if the match is sufficient
        """

        # Some robustness checks
        if len(self.ref.starlist) < 4:
            if verbose:
                print("Not enough stars in the reference catalog.")
            return
        if len(self.ukn.starlist) < 4:
            if verbose:
                print("Not enough stars in the unknown catalog.")
            return

        # First question : how many stars should match ?
        if len(self.ukn.starlist) < 5:  # Then we should simply try to get the smallest distance...
            minnident = 4
        else:
            minnident = max(4, min(8, len(self.ukn.starlist)/5.0))  # Perfectly arbitrary, let's see how it works

        # Hmm, arbitrary for now :
        minquaddist = 0.005

        # Let's start :
        if self.ref.quadlevel == 0:
            self.ref.makemorequads(verbose=verbose)
        if self.ukn.quadlevel == 0:
            self.ukn.makemorequads(verbose=verbose)

        while self.ok is False:
            # Find the best candidates
            cands = quad.proposecands(self.ukn.quadlist, self.ref.quadlist, n=4, verbose=verbose)

            if len(cands) != 0 and cands[0]["dist"] < minquaddist:
                # If no quads are available, we directly try to make more ones.
                for cand in cands:
                    # Check how many stars are identified...
                    nident = star.identify(self.ukn.starlist, self.ref.starlist, trans=cand["trans"],
                                           r=r, verbose=verbose, getstars=False)
                    if nident >= minnident:
                        self.trans = cand["trans"]
                        self.cand = cand
                        self.ok = True
                        break  # get out of the for

            if self.ok is False:
                # We add more quads...
                addedmorerefquads = self.ref.makemorequads(verbose=verbose)
                addedmoreuknquads = self.ukn.makemorequads(verbose=verbose)

                if addedmorerefquads is False and addedmoreuknquads is False:
                    break  # get out of the while, we failed.

        if self.ok:  # we refine the transform
            # get matching stars :
            (self.uknmatchstars, self.refmatchstars) = star.identify(self.ukn.starlist, self.ref.starlist,
                                                                     trans=self.trans, r=r, verbose=False,
                                                                     getstars=True)
            # refit the transform on them :
            if verbose:
                print("Refitting transform (before/after) :")
                print(self.trans)
            newtrans = star.fitstars(self.uknmatchstars, self.refmatchstars)
            if newtrans is not None:
                self.trans = newtrans
                if verbose:
                    print(self.trans)
            # Generating final matched star lists :
            (self.uknmatchstars, self.refmatchstars) = star.identify(self.ukn.starlist, self.ref.starlist,
                                                                     trans=self.trans, r=r, verbose=verbose,
                                                                     getstars=True)

            if verbose:
                print("I'm done!")

        else:
            if verbose:
                print("Failed to find transform!")

 
def run(ref, ukns, hdu=0, skipsaturated=False, r=5.0, n=500, sexkeepcat=False, sexrerun=True,
        verbose=True, polarMode=None, refpolar=False, camera=None):
    """
    Top-level function to identify transorms between images.
    Returns a list of Identification objects that contain all the info to go further.

    :param ref: path to a FITS image file that will act as the "reference".
    :type ref: string

    :param ukns: list of paths to FITS files to be "aligned" on the reference. **ukn** stands for unknown.
    :type ukns: list of strings

    :param hdu: The hdu of the fits files (same for all) that you want me to use. 0 is somehow "automatic".
    If multihdu, 1 is usually science.

    if the identification fails).

    :param skipsaturated: Should I skip saturated stars ?
    :type skipsaturated: boolean

    :param r: Identification radius in pixels of the reference image (default 5.0 should be fine).
    :type r: float
    :param n: Number of brightest stars of each image to consider (default 500 should be fine).
    :type n: int

    :param sexkeepcat: Put this to True if you want me to keep the SExtractor catalogs (in a dir "alipy_cats").
    :type sexkeepcat: boolean
    :param sexrerun: Put this to False if you want me to check if I have some previously kept catalogs
    (with sexkeepcat=True), instead of running SExtractor again on the images.
    :type sexrerun: boolean
    """

    if verbose:
        print(10*"#", " Preparing reference ...")
    ref = imgcat.ImgCat(ref, hdu=hdu)
    if refpolar:
        ref.makecat(rerun=sexrerun, keepcat=sexkeepcat, verbose=verbose, polarMode=polarMode, camera=camera)
    else:
        ref.makecat(rerun=sexrerun, keepcat=sexkeepcat, verbose=verbose, camera=camera)
    retCode = ref.makestarlist(skipsaturated=skipsaturated, n=n, verbose=verbose)
    if retCode:
        return None
    ref.makemorequads(verbose=verbose)

    identifications = []

    for ukn in ukns:

        if verbose:
            print(10*"#", "Processing %s" % (ukn))

        ukn = imgcat.ImgCat(ukn, hdu=hdu)
        ukn.makecat(rerun=sexrerun, keepcat=sexkeepcat, verbose=verbose, polarMode=polarMode, camera=camera)
        ukn.makestarlist(skipsaturated=skipsaturated, n=n, verbose=verbose)

        idn = Identification(ref, ukn)
        idn.findtrans(verbose=verbose, r=r)
        identifications.append(idn)

    return identifications
