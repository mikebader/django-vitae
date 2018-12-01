from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .base import DisplayableModel
from .managers import PrimaryPositionManager


class Award(DisplayableModel):
    """Award or honor earned."""

    name = models.CharField(max_length=200)
    organization = models.CharField(
        _('Granting institution or organization'), max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{}#award-{}'.format(reverse('cv:cv_list'), self.pk)

    objects = models.Manager()


class Degree(DisplayableModel):
    """Degree earned.

    Degrees are sorted in reverse order by ``end_date``.
    """

    degree = models.CharField(max_length=10)
    major = models.CharField(max_length=100, null=True, blank=True)
    date_earned = models.DateField(_('Date Earned'))
    institution = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(
        _('State or Province'), max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    honors = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-date_earned',)
        get_latest_by = 'date_earned'

    def __str__(self):
        return self.degree

    def get_absolute_url(self):
        return '{}#degree-{}'.format(reverse('cv:cv_list'), self.pk)

    objects = models.Manager()


class Position(DisplayableModel):
    """Position of employment or research experience.

    Positions are sorted by ``end_date``.

    In addition to default managers of ``DisplayableModel``, ``Position``
    also has a ``primarypositions`` manager that only returns positions
    for which ``primary_position==True``. This manager can be used, for
    example, to list positions in the heading of CVs.
    """

    title = models.CharField(max_length=100)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True,
        help_text=_('If current, set date to future (by default positions '
                    'will be ordered by end date')
    )
    project = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100)
    current_position = models.BooleanField(
        _('Current position?'), default=False,
        help_text=_('Are you currently in this position?'))
    primary_position = models.BooleanField(
        _('Primary position?'), default=False,
        help_text=_('Should this position be displayed as the main position '
                    '(e.g., on heading of CV)?')
    )

    def clean(self):
        """Ensure start date is before end date."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(
                    {'end_date': _('End date cannot be before start date')}
                )

    def get_absolute_url(self):
        return '{}#position-{}'.format(reverse('cv:cv_list'), self.pk)

    class Meta:
        ordering = ['-end_date', '-start_date']
        get_latest_by = 'end_date'

    def __str__(self):
        return '%s' % (self.title)

    objects = models.Manager()
    primary_positions = PrimaryPositionManager()
