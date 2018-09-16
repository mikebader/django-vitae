"""Tests Django-CV custom settings (:module:`cv.settings`)"""
# from django.core.exceptions import ValidationError
import django
from django.conf import settings
from django.dispatch import receiver
from django.test import TestCase
from django.test.utils import override_settings
from django.test.signals import setting_changed

import cv.settings


class SettingsTestCase(TestCase):
	"""
	Run tests of Django-CV :module:`cv.settings` module.
	"""

	def test_settings_choices_format(self):
		"""Test values given to custom choice sets"""
		CV_SERVICE_TYPES = [('a',1,1)]
		with self.assertRaises(ValueError):
			cv.settings.make_choice_list("CV_SERVICE_TYPES",CV_SERVICE_TYPES)

	def test_settings_publication_status_default(self):
		default_values = [0,1,20,30,35,40,50,55,60,99]
		default_names = ['INPREP','WORKING','SUBMITTED','REVISE',
						 'RESUBMITTED','CONDACCEPT','FORTHCOMING',
						 'INPRESS','PUBLISHED','RESTING']
		self.assertEqual(len(cv.settings.PUBLICATION_STATUS_CHOICES), 10)
		for (a,b) in zip(cv.settings.PUBLICATION_STATUS_CHOICES,default_values):
			self.assertEqual(a[0],b)
		for k in cv.settings.PUBLICATION_STATUS:
			name = k.replace("_STATUS","")
			i = default_names.index(name)
			self.assertEqual(cv.settings.PUBLICATION_STATUS[k],default_values[i])

	def test_settings_student_levels_default(self):
		default_values = [0,10,20]
		default_names = ['UNDERGRAD','MASTERS','DOCTORAL']
		self.assertEqual(len(cv.settings.STUDENT_LEVELS_CHOICES),3)
		for (a,b) in zip(cv.settings.STUDENT_LEVELS_CHOICES,default_values):
			self.assertEqual(a[0],b)
		for k in cv.settings.STUDENT_LEVELS:
			name = k.replace("_STUDENT","")
			i = default_names.index(name)
			self.assertEqual(cv.settings.STUDENT_LEVELS[k],default_values[i])

	def test_settings_service_types_default(self):
		default_values = [10,20,30,40,50,90]
		default_names = ['DEPARTMENT','SCHOOL','UNIVERSITY',
						 'DISCIPLINE','COMMUNITY','OTHER']
		self.assertEqual(len(cv.settings.SERVICE_TYPES_CHOICES),6)
		for (a,b) in zip(cv.settings.SERVICE_TYPES_CHOICES,default_values):
			self.assertEqual(a[0],b)
		for k in cv.settings.SERVICE_TYPES:
			name = k.replace("_SERVICE","")
			i = default_names.index(name)
			self.assertEqual(cv.settings.SERVICE_TYPES[k],default_values[i])

# @override_settings(CV_PUBLICATION_STATUS_CHOICES=(10,'INPREP','In preparation'))
class SettingsCustomTestCase(TestCase):
	
	def test_settings_publication_status_custom(self,**kwargs):
		"""Test function that creates custom publication status choices"""
		test_choices = [(10,'INPREP','In preparation')]
		custom_values = [10]
		custom_names = ["INPREP"]
		with self.settings(CV_PUBLICATION_STATUS_CHOICES=test_choices):
			(PUBLICATION_STATUS_CHOICES, 
				PUBLICATION_STATUS) = cv.settings.make_choice_list(
											'CV_PUBLICATION_STATUS_CHOICES',
											cv.settings.CV_PUBLICATION_STATUS_CHOICES,
											suffix="STATUS")
			self.assertEqual(len(PUBLICATION_STATUS_CHOICES),1)
			for k in PUBLICATION_STATUS:
				name = k.replace("_STATUS","")
				i = custom_names.index(name)
				self.assertEqual(PUBLICATION_STATUS[k],custom_values[i])
