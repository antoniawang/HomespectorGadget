
import argparse
import os
import glob
import subprocess

def invoke_test(test):
	with open('/dev/null', 'w') as nullout:
		retcode = subprocess.call(["python", "-v", test], stderr=nullout)
	return retcode

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--submit", help = "submit to master if passes tests", action = "store_true")
	parser.add_argument("-t", "--tests", help = "tests to run", nargs = "*", default = ["all"])

	args = parser.parse_args()

	# get tests to run
	path_to_tests = os.path.join(os.path.dirname(__file__), "test")
	tests_to_run = glob.glob(os.path.join(path_to_tests, "*.py"))

	test_results = {}
	for test in tests_to_run:
		if test.endswith("__init__.py"):
			continue
		test_results[os.path.basename(test)] = invoke_test(test)

	# check if everything passes
	results = test_results.values()
	for test, result in test_results.iteritems():
		print test, "had result", result
	if all(result == 0 for result in results):
		print "all tests passed"
		if args.submit:
			retcode = subprocess.call("git push orign master")
			if retcode == 0:
				print "submitted"
			else:
				print "something went wrong with submission"