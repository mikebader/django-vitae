from django.db import models
from django.db.models.functions import datetime
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .base import (VitaeModel, Collaborator, CollaborationModel,
                   StudentCollaborationModel)

from markdown import markdown


class InternalGrantManager(models.Manager):
    """Return grant objects for which source of funding is internal."""

    def get_queryset(self):
        return super(InternalGrantManager, self).get_queryset().filter(
            source=10
        ).filter(
            display=True
        )


class ExternalGrantManager(models.Manager):
    """Return grant objects for which source of funding is external."""

    def get_queryset(self):
        return super(ExternalGrantManager, self).get_queryset().filter(
            source=40
        ).filter(
            display=True
        )


class Grant(VitaeModel):
    """Create instance of funded grant."""

    INTERNAL = 10
    EXTERNAL = 40
    SOURCE = ((INTERNAL, 'Internal'),
              (EXTERNAL, 'External'))
    source = models.IntegerField(
        choices=SOURCE, help_text="Internal/external source of funding")
    agency = models.CharField(max_length=200, blank=True)
    agency_acronym = models.CharField(max_length=20, blank=True)
    division = models.CharField(max_length=200, blank=True)
    division_acronym = models.CharField(max_length=20, blank=True)
    grant_number = models.CharField(max_length=50, blank=True)
    amount = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    abstract = models.TextField(blank=True, null=True)
    abstract_html = models.TextField(blank=True, null=True, editable=False)

    collaborators = models.ManyToManyField(
        Collaborator, through='GrantCollaboration', related_name="grants")

    def get_pi(self):
        return self.collaborators.filter(grantcollaborator__is_pi=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.abstract_html = markdown(self.abstract)
        super(Grant, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        ordering = ['-is_current', '-start_date', '-end_date']

    def __str__(self):
        return self.title

    objects = models.Manager()
    internal_grants = InternalGrantManager()
    external_grants = ExternalGrantManager()


class GrantCollaboration(CollaborationModel):
    """Store object relating collaborators to grant."""

    grant = models.ForeignKey(
        Grant, related_name="collaboration", on_delete=models.PROTECT)
    is_pi = models.BooleanField(default=False)
    role = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return str(self.collaborator)


class Talk(VitaeModel):
    """Store object representing a talk."""

    abstract = models.TextField(blank=True)
    # article_from_talk = models.OneToOneField(
    #   Article, null=True, blank=True,on_delete=models.CASCADE)
    collaborator = models.ManyToManyField(Collaborator, blank=True)
    grants = models.ManyToManyField(Grant, blank=True)

    abstract_html = models.TextField(editable=False, blank=True)
    latest_presentation_date = models.DateField(
        editable=False, blank=True, null=True)
    created = models.DateField(auto_now_add=True, blank=True)
    modified = models.DateField(auto_now=True, blank=True)

    class Meta:
        ordering = ['-latest_presentation_date']

    def __str__(self):
        return self.short_title

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.abstract_html = markdown(self.abstract)
        super(Talk, self).save(force_insert, force_update, *args, **kwargs)

    def get_absolute_url(self):
        return reverse('cv:talk_object_detail', kwargs={'slug': self.slug})

    def get_latest_presentation(self):
        return self.presentations.all()[0]

    objects = models.Manager()


class Presentation(models.Model):
    """Create an instance in which a talk was given.

    This model creates separate objects for each time the same talk was given.
    """

    INVITED = 10
    CONFERENCE = 20
    WORKSHOP = 30
    KEYNOTE = 40
    TYPE = ((INVITED, 'Invited'),
            (CONFERENCE, 'Conference'),
            (WORKSHOP, 'Workshop'),
            (KEYNOTE, 'Keynote'))
    talk = models.ForeignKey(
        Talk, related_name='presentations', on_delete=models.CASCADE)
    presentation_date = models.DateField()
    type = models.IntegerField(choices=TYPE)
    event = models.CharField(max_length=150)
    event_acronym = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-presentation_date']

    def __str__(self):
        return '%s; %s (%s %s)' % (
            self.talk, self.event, self.presentation_date.month,
            self.presentation_date.year)

    def save(self, *args, **kwargs):
        """Save latest presentation date in related talk if instance is later
        than current latest presentation date."""
        try:
            delta = self.presentation_date - self.talk.latest_presentation_date
            assert delta < datetime.timedelta(0)
        except:
            self.talk.latest_presentation_date = self.presentation_date
            self.talk.save()
        super(Presentation, self).save(*args, **kwargs)


class OtherWriting(VitaeModel):
    """Create an instance of writing in venues other than
    traditional scholarly venues.

    Default ordering by ``type`` and then ``date`` in descending order.
    """

    type = models.CharField(
        max_length=100, blank=True,
        help_text=_("Genre of writing (e.g., 'book review','op ed', "
                    "'blog post') that can be used for grouping contributions "
                    "by type."))
    abstract = models.TextField(blank=True)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    pages = models.CharField(
        _('Pages or section'), max_length=200, null=True, blank=True)
    url = models.URLField(blank=True)
    place = models.CharField(max_length=100, blank=True)
    volume = models.CharField(max_length=20, blank=True)
    issue = models.CharField(max_length=20, blank=True)

    abstract_html = models.TextField(blank=True, editable=False)

    class Meta:
        """Orders other writings in reverse chronological order."""
        ordering = ['-date']

    def __str__(self):
        """Returns string representation of other writing."""
        return self.short_title

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """Saves abstract in html format."""
        self.abstract_html = markdown(self.abstract)
        super(OtherWriting, self).save(
            force_insert, force_update, *args, **kwargs)

    objects = models.Manager()


class Dataset(VitaeModel):
    """Stores instance representing a dataset."""

    authors = models.ManyToManyField(
        Collaborator, through='DatasetAuthorship', related_name='datasets')
    pub_date = models.DateField(
        _('Publication date'), blank=True, null=True)
    version_number = models.CharField(
        _('Version number'), max_length=80, blank=True)
    format = models.CharField(
        _('Format'), max_length=150, blank=True,
        help_text=_('Form of data (e.g., \'Datafile and Codebook\''
                    ' or \'Datafile\')')
    )
    producer = models.CharField(
        _('Producer'), max_length=180, blank=True)
    producer_place = models.CharField(
        _('Producer location'), max_length=100, blank=True, null=True)
    distributor = models.CharField(
        _('Distributor'), max_length=180, blank=True)
    distributor_place = models.CharField(
        _('Distributor location'), max_length=100, blank=True, null=True)
    retrieval_url = models.URLField(
        _('Retrieval URL'), blank=True,
        help_text=_('Used for URL linked to dataset'))
    available_from_url = models.URLField(
        _('Available from URL'), blank=True,
        help_text=_('Used to link to a download page'))
    doi = models.CharField(
        _('DOI'), max_length=100, blank=True, null=True)

    def get_absolute_url(self):
        """"Returns reverse URL for an instance of a dataset."""
        return reverse(
            'cv:item_detail',
            kwargs={'model_name': self._meta.model_name, 'slug': self.slug})

    def __str__(self):
        """String representation of a dataset instance."""
        return '%s' % self.short_title

    objects = models.Manager()


class DatasetAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating creators of dataset to a dataset instance."""

    dataset = models.ForeignKey(
        Dataset, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['dataset', 'display_order']
        unique_together = ('dataset', 'display_order')
