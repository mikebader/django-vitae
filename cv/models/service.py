from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import DisplayableModel, Journal
from .managers import ServiceManager

from cv.settings import SERVICE_TYPES_CHOICES


class Service(DisplayableModel):

    """Add object to record service commitments."""

    role = models.CharField(max_length=200)
    group = models.CharField(
        max_length=200, blank=True, null=True,
        help_text=_('Group or committee on which service was performed'))
    organization = models.CharField(
        _('Organization or department'), max_length=200)
    type = models.IntegerField(choices=SERVICE_TYPES_CHOICES)
    start_date = models.DateField(
        blank=True, null=True,
        help_text=_("Leave blank of one-time service"))
    end_date = models.DateField(
        blank=True, null=True,
        help_text=_("Leave blank if service is ongoing"))
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-end_date', '-start_date']

    def __str__(self):
        return '%s: %s (%s)' % (self.role, self.group, self.organization)

    def clean(self):
        check = [self.start_date, self.end_date]
        if not any(check):
            raise ValidationError(_('Must select at least one date field.'))

    objects = models.Manager()
    displayable = ServiceManager()


# Reviews
class JournalService(DisplayableModel):
    """Objects representing journals for which one has reviewed."""

    journal = models.OneToOneField(
        Journal, on_delete=models.CASCADE, blank=True, null=True, unique=True)
    is_reviewer = models.BooleanField(default=True)

    class Meta:
        ordering = ['journal']

    def __str__(self):
        return '%s' % self.journal.title

    objects = models.Manager()
