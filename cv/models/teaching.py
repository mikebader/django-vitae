from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import DisplayableModel

from cv.settings import STUDENT_LEVELS_CHOICES, TERMS_CHOICES

from markdown import markdown


class Course(DisplayableModel):
    """Instance of a class or course prepared."""

    title = models.CharField(_('Title'), max_length=150)
    short_title = models.CharField(max_length=80)
    slug = models.SlugField(
        unique=True, help_text=_('Automatically built from short title'),
        null=True, default=None)
    slug = models.SlugField(_('Slug'), unique=True)
    short_description = models.TextField(_('Short description'), blank=True)
    full_description = models.TextField(_('Full description'), blank=True)
    student_level = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, null=True, blank=True)

    # Fields used to store html from Markdown input
    short_description_html = models.TextField(editable=False)
    description_html = models.TextField(editable=False)

    last_offered = models.DateField(_('Last offered'), null=True, blank=True)
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
        Course, on_delete=models.CASCADE, verbose_name=_('Course'),
        related_name='offerings')
    term = models.IntegerField(_('Term'), choices=TERMS_CHOICES)
    start_date = models.DateField(_('Start date'), blank=True)
    end_date = models.DateField(_('End date'), blank=True)
    institution = models.CharField(
        _('Institution'), max_length=100, blank=True)
    course_number = models.CharField(
        _('Course number'), max_length=50, blank=True)
    is_current_offering = models.BooleanField(
        _('Is current offering?'), default=False)

    def __str__(self):
        return u"%s (%s %s)" % (
            str(self.course), self.get_term_display(), self.start_date.year)

    class Meta:
        ordering = ['-start_date']

    objects = models.Manager()
