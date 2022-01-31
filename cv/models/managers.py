from django.db import models
from django.db.models import F
from cv.settings import SERVICE_TYPES


class DisplayManager(models.Manager):
    """Returns displayable objects from models."""

    def get_queryset(self):
        """Return objects for which field
        ``display`` has been set to ``True``."""
        return super(DisplayManager, self).get_queryset().filter(display=True)


class PublicationManager(DisplayManager):
    """Class to manage publications.

    This class subclasses ``DisplayManager`` and includes the default
    queryset of all displayable objects. In addition, it provides
    three methods: ``published``, ``revise``, and ``inprep`` to return
    querysets of publications at stages in the publication process.
    """

    @property
    def management_lists(self):
        return ['published', 'revise', 'inprep']

    def published(self):
        """Return queryset of articles accepted for publication
        or published.
        """
        return self.filter(
            is_published__exact=True).filter(
            display__exact=True).order_by(
                F('pub_date').desc(nulls_first=True)
            )

    def revise(self):
        """Return queryset of articles in revision process."""
        return self.filter(
            is_inrevision__exact=True).filter(
            display__exact=True).order_by(
            '-submission_date')

    def inprep(self):
        """Return queryset of articles being prepared for submission."""
        return self.filter(
            is_inprep__exact=True).filter(
            display__exact=True)


class GrantManager(DisplayManager):
    """Class to manage grants.

    This class subclasses ``DisplayManager`` and includes the default
    queryset of all displayable objects. In addition, it provides two
    methods: ``internal_grants`` and ``external_grants`` for different
    grant sources.
    """

    management_lists = ['internal_grants',
                        'external_grants']

    def internal_grants(self):
        return self.filter(source=10).filter(display=True)

    def external_grants(self):
        return self.filter(source=40).filter(display=True)


class ServiceManager(DisplayManager):
    """Class to manage service work.

    This class subclasses ``DisplayManager`` and includes the default
    queryset of all displayable objects. In addition, it provides
    three methods: ``department_services``, ``university services``, and
    ``discipline_services`` for service work to different institutions.
    """

    management_lists = ['department',
                        'university',
                        'discipline']

    def department(self):
        return self.filter(
            type__in=[
                SERVICE_TYPES['DEPARTMENT_SERVICE'],
            ]).filter(display=True).order_by(
                F('end_date').desc(nulls_first=True)
            )

    def university(self):
        return self.filter(
            type__in=[
                SERVICE_TYPES['UNIVERSITY_SERVICE'],
                SERVICE_TYPES['SCHOOL_SERVICE']
            ]).filter(display=True).order_by(
                F('end_date').desc(nulls_first=True)
            )

    def discipline(self):
        return self.filter(
            type=SERVICE_TYPES['DISCIPLINE_SERVICE']
            ).filter(display=True).order_by(
                F('end_date').desc(nulls_first=True)
            )


class PositionManager(models.Manager):
    """Manager positions ordered by date."""

    def get_queryset(self):
        return super(PositionManager, self).get_queryset().order_by(
            F('end_date').desc(nulls_first=True)
        )


class PrimaryPositionManager(models.Manager):
    """Manages positions used in heading of CV.

    Returns a queryset of positions in which ``primary_position`` has been set
    to ``True``.
    """

    def get_queryset(self):
        """Return positions user indicated as 'primary' positions."""
        return super(PrimaryPositionManager, self).get_queryset().filter(
            primary_position=True)

