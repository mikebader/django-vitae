from django.db import models
from django.utils.translation import gettext_lazy as _

from cv.settings import STUDENT_LEVELS_CHOICES

from .base import DisplayableModel


class Person(models.Model):

    first_name = models.CharField('First (given) name', max_length=100)
    last_name = models.CharField('Last (family) name', max_length=100)
    middle_initial = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=100, blank=True)
    url = models.URLField(_('URL'), blank=True)
    email = models.EmailField(unique=True, null=True, default=None)

    class Meta:
        abstract = True

    def __str__(self):
        name = '%s, %s %s' % (
            self.last_name,
            self.first_name,
            self.middle_initial)
        return name.strip()


class Collaborator(Person):
    """Representation of collaborator on publications or projects.

    Collaborators represent all people listed in entries of a CV that are
    not the user. Django-Vitae uses the ``email`` attribute to identify
    and manage collaborators internally and must, therefore, be unique
    to each collaborator.

    Collaborators are ordered alphabetically by last name by default.
    """

    institution = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    alternate_email = models.EmailField(blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']


class Student(Person, DisplayableModel):
    """Representation of student."""

    student_level = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, null=True, blank=True
    )
    role = models.CharField(max_length=200, null=True)
    thesis_title = models.CharField(max_length=200, null=True, blank=True)
    is_current_student = models.BooleanField(default=True)
    graduation_date = models.DateField(null=True, blank=True)
    first_position = models.CharField(max_length=200, null=True, blank=True)
    current_position = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['student_level', 'graduation_date']

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

    objects = models.Manager()
