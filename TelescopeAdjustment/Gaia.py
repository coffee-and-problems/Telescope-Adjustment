import gzip
from astropy.io.votable import parse_single_table
from os import path
import math
import csv

from astropy import coordinates
import astropy.units as u
from astroquery.gaia import Gaia

class Gaia_star():
    def __init__(self, ra, dec, flux):
        self.ra = ra
        self.dec = dec
        self.flux = flux


class Gaia_data():
    """Class to work with Gaia database"""
    def __init__(self, fov, matrix_pixels):
        self.fov = fov
        self.matrix_pixels = matrix_pixels

    def make_star_list(self, table):
        """
        Parses ra, dec, flux columns to list of Gaia_star
            :param table: Gaia table
            :type table:
        """
        RA = table['ra']
        DEC = table['dec']
        FLUX = table['phot_g_mean_flux']

        if len(RA) != len(DEC) and len(RA) != len(FLUX):
            raise RuntimeError('Something is not quite right with Gaia table') from exc

        stars = []
        for i in range(len(RA)):
            stars.append(Gaia_star(RA[i], DEC[i], FLUX[i]))

        return stars

    def download_gaia_results(self, coords, keep_on_disk):
        """
        Sends a request to https://app.aavso.org to get information on a specific object.
            :param coords: coords in degrees
            :type coords: tuple<float, float>
            :param fov: field of view in arcmins
            :type fov: float
            :param keep_on_disk: should Gaia VOTables be saved on disk?
            :type keep_on_disk: bool
        """

        #async is an overkill for 500 rows but let's stick with that for now
        query = "SELECT TOP 500 gaia_source.ra,gaia_source.dec,gaia_source.phot_g_mean_flux,gaia_source.phot_g_mean_mag \
        FROM gaiadr2.gaia_source \
        WHERE \
        CONTAINS(\
	        POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec),\
	        CIRCLE('ICRS',{0},{1},{2})\
        )=1  AND  (gaiadr2.gaia_source.phot_rp_mean_mag<=17);".format(coords[0], coords[1], self.fov/120)
        job = Gaia.launch_job_async(query, dump_to_file=keep_on_disk)
        table = job.get_results()

        return self.make_star_list(table)

    def parse_gaia_results(self, path_to_table):
        """
        Parses an existing .gz archive with VOTable
            :param path_to_table: path to Gaia .gz archive
            :type path_to_table: string
        """
        a_file = gzip.open(path_to_table, "rb")
        table = parse_single_table(a_file)

        return self.make_star_list(table.array)
        
    def get_ratio(self, ra_dec_center):
        """
        Returns pixel/degree ratio as (ratio_RA, ratio_Dec)
            :param arcmin_fov: field of view in arcmins (ex 9.5)
            :type arcmin_fov: float
            :param pix_fov: field of view in pixels (ex 600)
            :type pix_fov: int
            :param ra_dec_center: ra and dec of the center in degrees (ex (299.99, 65.18))
            :type ra_dec_center: tuple<float, float>
        """
        ratio_y = self.matrix_pixels / self.fov * 60
        ratio_x = self.matrix_pixels / self.fov * 60 * math.cos(math.radians(ra_dec_center[1]))
        return (ratio_x, ratio_y)

    def map(self, star_list, ra_dec_center):
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
        ratio_x, ratio_y = self.get_ratio(ra_dec_center)

        zero_ra = ra_dec_center[0] - self.matrix_pixels/2/ratio_x
        zero_dec = ra_dec_center[1]- self.fov/120

        maped_star_list = []
        for star in star_list:
            x = (star.ra - zero_ra) * ratio_x
            y = (star.dec - zero_dec) * ratio_y
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
                file.write(f'{i+1:{10}}{star.ra:{11}.{4}}{star.dec:{11}.{4}}{star.flux:{13}.{4}}{1.09:{9}}{0:{4}}{1.0:{9}}\n')

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
        ra = float(RA[0])*15 + float(RA[1])*0.25 + float(RA[2])*1/240
        DEC = dec_string.split()
        dec = float(DEC[0]) + float(DEC[1])*1/60 + float(DEC[2])*1/3600
        return (ra, dec)

    def get_box(self, ra_dec_center):
        """
        Returns ((ra_start, ra_end),(dec_start,dec_end)) in gedrees
            :param ra_string: RA (ex. 04 19 45)
            :type ra_string: string
            :param dec_string: dec (ex. -05 47 22)
            :type dec_string: string
            :param fov: field of view in arcmins (ex 9.5)
            :type fov: float
        """
        ratio_x, ratio_y = self.get_ratio(self.fov, ra_dec_center)

        start_ra = ra_dec_center[0] - self.matrix_pixels/2/ratio_x
        start_dec = ra_dec_center[1]- self.fov/120
        end_ra = ra_dec_center[0] + self.matrix_pixels/2/ratio_x
        end_dec = ra_dec_center[1] + self.fov/120
        return ((start_ra, end_ra), (start_dec, end_dec))


    def make_ref_cat(self, name, ra, dec, gaia_table=None, keep_tabel=False):
        """
        Saves reference SExtracror catalog of the object.
            :param ra_string: RA (ex. 04 19 45)
            :type ra_string: string
            :param dec_string: dec (ex. -05 47 22)
            :type dec_string: string
            :param fov: field of view in arcmins (ex 9.5)
            :type fov: float
            :param gaia_table: path to Gaia .gz archive. If none we'll download our own (will NOT be saved on disk)
            :type gaia_table: string
            :param keep_tables: should Gaia VOTables be saved on disk?
            :type keep_tables: bool
        """
        coords = (ra, dec)

        if gaia_table is None:
            s1 = self.download_gaia_results(coords, keep_tabel)
        else:
            s1 = self.parse_gaia_results(gaia_table)
        s2 = self.map(s1, coords)
        self.save_sex_cat(f"{name}alipysexcat", s2)

    def make_ref_cats_for_all(self, csv_file, keep_gaia_tables=False):
        """
        Saves reference SExtracror catalog of the objects described in a csv file.
            :param csv_file: path to .csv file containing as follows: name of the object, ra, dec
            :type csv_file: string
            :param fov: field of view in arcmins (ex 9.5)
            :type fov: float
            :param keep_gaia_tables: should Gaia VOTables be saved on disk?
            :type keep_gaia_tables: bool
        """
        with open(csv_file) as file:
            reader = csv.reader(file, skipinitialspace=True)
            next(reader, None)
            for source in reader:
                field = self.make_ref_cat(source[0], source[1], source[2], keep_tabel=keep_gaia_tables)