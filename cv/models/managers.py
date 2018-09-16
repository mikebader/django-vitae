from django.db import models


class DisplayManager(models.Manager):
    """Returns displayable objects from models."""

    def get_queryset(self):
        """Return objects for which field
        ``display`` has been set to ``True``."""
        return super(DisplayManager, self).get_queryset().filter(display=True)


class PublishedManager(models.Manager):
    """Return queryset of articles accepted for publication or published."""

    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(
            is_published__exact=True).filter(
            display__exact=True).order_by(
            '-pub_date')


class InprepManager(models.Manager):
    """Return queryset of articles being prepared for submission."""

    def get_queryset(self):
        return super(InprepManager, self).get_queryset().filter(
            is_inprep__exact=True).filter(
            display__exact=True)


class ReviseManager(models.Manager):
    """Return queryset of articles in revision process."""

    def get_queryset(self):
        return super(ReviseManager, self).get_queryset().filter(
            is_inrevision__exact=True).filter(
            display__exact=True).order_by(
            '-submission_date')
