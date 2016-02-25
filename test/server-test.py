
import os
import sys
import subprocess
import logging
import unittest


my_dir = os.path.dirname(__file__)  # get the directory of this file
one_level_up = os.path.join(my_dir, "..")  # go one level up
one_level_up_absolute = os.path.abspath(one_level_up)  # get the absolute path of the directory above me
sys.path.append(one_level_up_absolute)  # add that path to my import path

import server # this is what we're testing


class TestServerRuns(unittest.TestCase):

	def setUp(self):
		self.cwd = os.getcwd()
		os.chdir(one_level_up_absolute)
		self.process = subprocess.Popen(["python", "server.py"])

	def tearDown(self):
		self._kill_process()
		os.chdir(self.cwd)

	def _kill_process(self):
		with open('/dev/null', 'w') as nullout:
			subprocess.call(["kill", "-9", str(self.process.pid)], stdout=nullout, stderr=nullout)

	def test_01_running(self):
		self.assertIsNone(self.process.poll())

	def test_02_kill_server(self):
		self._kill_process()
		self.assertIsNotNone(self.process.poll())


if __name__ == "__main__":
	unittest.main()
