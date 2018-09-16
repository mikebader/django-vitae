"""Tests for Django-CV Models"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.settings import PUBLICATION_STATUS, STUDENT_LEVELS
from cv.models import Chapter, ChapterAuthorship, ChapterEditorship, \
    Collaborator

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase
