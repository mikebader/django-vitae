from django.apps import AppConfig

import cv

class CvConfig(AppConfig):
    name = 'cv'
    verbose_name = 'CV'
    
    def ready(self):
    	import cv.signals
