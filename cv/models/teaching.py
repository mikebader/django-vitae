from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import (DisplayableModel)

from cv.settings import STUDENT_LEVELS_CHOICES, TERMS_CHOICES

from markdown import markdown


class Student(DisplayableModel):

    """Add object to represent students that have been advised."""

    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
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


class Course(DisplayableModel):
    """Instance of a class or course prepared."""

    title = models.CharField(_('title'), max_length=150)
    slug = models.SlugField(_('slug'), blank=True)
    short_description = models.TextField(_('short description'), blank=True)
    full_description = models.TextField(_('full description'), blank=True)
    student_level = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, null=True, blank=True)

    # Fields used to store html from Markdown input
    short_description_html = models.TextField(editable=False)
    description_html = models.TextField(editable=False)

    last_offered = models.DateField(_('last offered'), null=True, blank=True)
    # is_current_offering = models.BooleanField(
    #     _('is current offering?'), default=False)

    class Meta:
        ordering = ['-last_offered', 'title']

    def __str__(self):
        return("{0}".format(self.title))

    def save(self, force_insert=False, force_update=False):
        """Prepares html versions and records last offering.

        Saves the markdown input into html to reduce load on
        templates and updates `last_offered` field to latest
        `CourseOffering` instance associated with the class.
        """
        self.short_description_html = markdown(self.short_description)
        self.full_description_html = markdown(self.full_description)
    #     # self.last_offered = self.courseoffering_set.filter(
    #     #     start_date__lte=timezone.now()).aggregate(
    #     #     last_offering=Max('end_date'))['last_offering']
        super(Course, self).save(force_insert, force_update)

    objects = models.Manager()


class CourseOffering(models.Model):
    """Instance of a term when a course was taught."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name=_('course'),
        related_name='offerings')
    term = models.IntegerField(_('term'), choices=TERMS_CHOICES)
    start_date = models.DateField(_('start date'), blank=True)
    end_date = models.DateField(_('end date'), blank=True)
    institution = models.CharField(
        _('institution'), max_length=100, blank=True)
    course_number = models.CharField(
        _('course number'), max_length=50, blank=True)
    is_current_offering = models.BooleanField(
        _('is current offering?'), default=False)

    def __str__(self):
        return u"%s (%s %s)" % (
            str(self.course), self.get_term_display(), self.start_date.year)

    class Meta:
        ordering = ['-start_date']

    objects = models.Manager()
