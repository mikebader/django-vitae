#!/usr/bin/env python
import coverage
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
	if len(sys.argv) < 2:
		cov = coverage.coverage(source=['cv'], omit=['*/tests/*'])
		cov.erase()
		cov.start()
	os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
	for arg in sys.argv[1:]:
		settings.NOSE_ARGS.append(arg)
	django.setup()
	TestRunner = get_runner(settings)
	test_runner = TestRunner()
	failures = test_runner.run_tests(["tests"])
	if len(sys.argv) < 2:
		cov.stop()
		cov.save()
		cov.report()
		cov.html_report(directory="tests/html")
	sys.exit(bool(failures))
