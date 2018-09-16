from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from cv.settings import CV_PERSONAL_INFO

def cv_personal_info(request):
	"""Add information about person to CV requests"""
	return {'cv_personal_info': CV_PERSONAL_INFO}

def site(request):
        """Add site to context for CV requests"""
        return {'site':get_current_site(request)}