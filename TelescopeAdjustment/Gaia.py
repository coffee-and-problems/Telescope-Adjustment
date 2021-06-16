import gzip
from astropy.io.votable import parse_single_table
from os import path


class Gaia_star():
    def __init__(self, ra, dec, flux):
        self.ra = ra
        self.dec = dec
        self.flux = flux


class Gaia(object):
    """Class to work with Gaia database"""

    def parse_gaia_results(self, path_to_table):
        """
        Sends a request to https://app.aavso.org to get information on a specific object.
            :param path_to_table: path to Gaia .gz archive
            :type path_to_table: string
        """
        a_file = gzip.open(path_to_table, "rb")
        table = parse_single_table(a_file)
        RA = table.array['ra']
        DEC = table.array['dec']
        FLUX = table.array['phot_g_mean_flux']

        if len(RA) != len(DEC) and len(RA) != len(FLUX):
            raise RuntimeError('Something is not quite right with Gaia table') from exc

        stars = []
        for i in range(len(RA)):
            stars.append(Gaia_star(RA[i], DEC[i], FLUX[i]))

        return stars

    def map(self, star_list, arcmin_fov, pix_fov, ra_dec_center):
        """
        Returns star list with coordanates in pixelsas like if they were observed by a telescope.
            :param star_list: list of Gaia_star objects
            :type star_list: list<Gaia_star>
            :param arcmin_fov: field of view in arcmins (ex 9.5)
            :type arcmin_fov: float
            :param pix_fov: field of view in pixels (ex 600)
            :type pix_fov: int
            :param ra_dec_center: ra and dec of the center in degrees (ex (299.99, 65.18))
            :type ra_dec_center: tuple<float, float>
        """
        ratio = 3601.44#pix_fov/arcmin_fov

        zero_ra = ra_dec_center[0] - arcmin_fov/60
        zero_dec = ra_dec_center[1]- arcmin_fov/120


        maped_star_list = []
        for star in star_list:
            x = (-zero_ra + star.ra) * ratio/2
            y = (-zero_dec + star.dec) * ratio
            #x = int(round((-zero_ra + star.ra * 60) * ratio))
            #y = int(round((-zero_dec + star.dec * 60) * ratio))
            maped_star_list.append(Gaia_star(x, y, star.flux))
        return maped_star_list
         
    def save_sex_cat(self, name, stars):
        file_path = path.join("alipy_cats", "{0}".format(name))
        with open(file_path, 'w') as file:
            file.write("#   1 NUMBER          Running object number\n")
            file.write("#   2 X_IMAGE         Object position along x                         [pixel]\n")
            file.write("#   3 Y_IMAGE         Object position along y                         [pixel]\n")
            file.write("#   4 FLUX_AUTO       Flux within a Kron-like elliptical aperture     [count]\n")
            file.write("#   5 FWHM_IMAGE      FWHM assuming a gaussian core                   [pixel]\n")
            file.write("#   6 FLAGS           Extraction flags\n")
            file.write("#   7 ELONGATION      A_IMAGE/B_IMAGE\n")

            for i in range(len(stars)):
                star = stars[i]
                #file.write(f'{i+1:{10}}{star.ra:{11}}{star.dec:{11}}{star.flux:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')
                file.write(f'{i+1:{10}}{star.ra:{11}.{5}}{star.dec:{11}.{5}}{star.flux:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')

    def pet_sexy_cat(self):
        print("      \\    /\\\n       )  ( \')\n      (  /  )\n meaw  \(__)|")



gaia = Gaia()
s1 = gaia.parse_gaia_results("17.gz")
s2 = gaia.map(s1, 10, 600, (299.9991667, 65.1483333))
gaia.save_sex_cat("Q1959alipysexcat", s2)
pass