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
            x = (-zero_ra + star.ra) * ratio/2 * 5/6
            y = (-zero_dec + star.dec) * ratio
            maped_star_list.append(Gaia_star(x, y, star.flux))
        return maped_star_list
         
    def save_sex_cat(self, name, stars):
        """
        Saves list of Gaia_star to file to match SExtractor catalog format
            :param name: name of the file to be created
            :type name: string
            :param stars: list of Gaia_star objects
            :type stars: list<Gaia_star>
        """
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
                file.write(f'{i+1:{10}}{star.ra:{11}.{3}}{star.dec:{11}.{3}}{star.flux:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')

    def pet_sexy_cat(self):
        print("      \\    /\\\n       )  ( \')\n      (  /  )\n meaw  \(__)|")

    def coords_to_deg(self, ra_string, dec_string):
        """
        Returns (RA Dec) tuple in degrees
            :param ra_string: RA (ex. 04 19 45)
            :type ra_string: string
            :param dec_string: dec (ex. -05 47 22)
            :type dec_string: string
        """
        RA = ra_string.split()
        ra = float(RA[0])*15 + float(RA[1])*0.25 + float(RA[2])*0.0042
        DEC = dec_string.split()
        dec = float(DEC[0]) + float(DEC[1])*0.0167 + float(DEC[2])*0.0003
        return (ra, dec)



