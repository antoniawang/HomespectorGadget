
import os.path
import sys
import unittest

my_dir = os.path.dirname(__file__)  # get the directory of this file
one_level_up = os.path.join(my_dir, "..")  # go one level up
one_level_up_absolute = os.path.abspath(one_level_up)  # get the absolute path of the directory above me
sys.path.append(one_level_up_absolute)  # add that path to my import path

import utils # this is what we're testing

class TestCreateAddressUrl(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_parsing_full(self):
		input_str = "1600 Pennsylvania Avenue, Washington, D.C. 20500"
		address_url, citystate_zip_url, _ = utils.create_address_url(input_str)

		self.assertEqual(address_url, "1600+Pennsylvania+Avenue")
		self.assertEqual(citystate_zip_url, "Washington%2C+D.C.+20500")

	def test_parsing_partial(self):
		input_str = "1600 Pennsylvania Ave, 20500"
		address_url, citystate_zip_url, _ = utils.create_address_url(input_str)

		self.assertEqual(address_url, "1600+Pennsylvania+Ave")
		self.assertEqual(citystate_zip_url, "%2C++20500")

class TestGetZoomLevel(unittest.TestCase):

	def setUp(self):
		self.imgwidth = 1024
		self.imgheight = 650

	def tearDown(self):
		pass

	def test_opt_zoom_far(self):
		lat_max = 37.778078 
		lat_min = 37.531389 
		lon_max = -122.3610777 
		lon_min = -122.5068727
		
		zoom_level = utils.get_zoom_level(lat_max, lat_min, lon_max, lon_min, self.imgheight, self.imgwidth)
		self.assertEqual(zoom_level, 11.0)

	def test_opt_zoom_close(self):
		lat_min = 37.778078 
		lat_max = 37.7790522 
		lon_min = -122.5075327
		lon_max = -122.5038727
		
		zoom_level = utils.get_zoom_level(lat_max, lat_min, lon_max, lon_min, self.imgheight, self.imgwidth)
		self.assertEqual(zoom_level, 18.0)

	def test_opt_zoom_error(self):
		lat_min = 37.778078 
		lat_max = 37.7780522 
		lon_min = -122.5075327
		lon_max = -122.5068727
	
		# to catch that it fails with this error
		with self.assertRaises(ValueError):	
			zoom_level = utils.get_zoom_level(lat_max, lat_min, lon_max, lon_min, self.imgheight, self.imgwidth)

if __name__ == "__main__":
	unittest.main()