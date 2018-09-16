"""Defines Django-CV publication models."""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from cv.utils import check_isbn

from markdown import markdown

from .base import DisplayableModel, VitaePublicationModel, Journal, \
    Collaborator, CollaborationModel, StudentCollaborationModel
from .works import Grant, Talk


class Article(VitaePublicationModel):
    """Store instance representing an article."""
    abstract = models.TextField(blank=True)
    authors = models.ManyToManyField(
        Collaborator, through='ArticleAuthorship', related_name='articles')
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, blank=True, null=True)
    volume = models.CharField(max_length=20, blank=True)
    issue = models.CharField(max_length=20, blank=True)
    start_page = models.CharField(max_length=10, blank=True)
    end_page = models.CharField(max_length=10, blank=True)
    series = models.CharField(max_length=100, blank=True)
    number = models.CharField(max_length=15, blank=True)
    url = models.URLField(_('URL to published article'), blank=True)
    doi = models.CharField(_('DOI'), max_length=200, blank=True)
    pmcid = models.CharField(
        'PMCID', max_length=40, blank=True,
        help_text=_('PubMed Central reference number (for more info see: '
                    'https://publicaccess.nih.gov/include-pmcid-citations.htm#Difference)'))
    pmid = models.CharField(
        'PMID', max_length=40, blank=True,
        help_text=_('PubMed Central reference number (for more info see: '
                    'https://publicaccess.nih.gov/include-pmcid-citations.htm#Difference)'))

    abstract_html = models.TextField(blank=True, editable=False)

    grants = models.ManyToManyField(Grant, blank=True)
    talks = models.ManyToManyField(Talk, blank=True)

    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     """Saves instance of article."""
    #     super(Article, self).save(force_insert, force_update, *args, **kwargs)

    # class Meta:
    #     get_latest_by = 'pub_date'
        # permissions = (
        #    ("can_view_nonpublic", "Can view non-public articles"),
        #    )

    # def get_primary_files(self):
    #     """Return queryset of :class:`cv.models.CVFile` objects designated
    #     as "primary files" associated with article."""
    #     return self.files.filter(is_primary__exact=True)

    objects = models.Manager()


class ArticleAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to article."""

    article = models.ForeignKey(
        Article, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['article', 'display_order']
        unique_together = ('article', 'display_order')


class Book(VitaePublicationModel):
    """Store instance representing a book."""

    authors = models.ManyToManyField(
        Collaborator, through='BookAuthorship', related_name="books")
    abstract = models.TextField(blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    place = models.CharField(max_length=100, blank=True)
    volume = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=100, blank=True)
    series_number = models.CharField(max_length=10, blank=True)
    num_pages = models.IntegerField(
        _('Number of pages'), blank=True, null=True)
    isbn = models.CharField(
        _('ISBN'), max_length=20, blank=True,
        validators=[RegexValidator(r'^\d+[0-9\-]+[Xx0-9]$')])
    url = models.URLField(_('URL'), blank=True)
    grants = models.ManyToManyField(Grant, blank=True)

    abstract_html = models.TextField(blank=True, editable=False)

    def add_edition(self, **kwargs):
        """Add edition to book."""
        if 'edition' not in kwargs.keys():
            raise ValidationError(_("The field 'edition' cannot be blank"))
        kwargs['book'] = self
        BookEdition.objects.create(**kwargs)

    def get_editions(self):
        """Return queryset of all editions associated with book."""
        return self.editions.all().order_by('-pub_date')

    objects = models.Manager()


class BookAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store authorship object relating collaborators to book."""

    book = models.ForeignKey(
        Book, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['book', 'display_order']
        unique_together = ('book', 'display_order')


class BookEdition(DisplayableModel):
    """Store edition information of a book."""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="editions")
    edition = models.CharField(max_length=50)
    pub_date = models.DateField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True)
    place = models.CharField(blank=True, null=True, max_length=100)
    num_pages = models.IntegerField('Number of pages', blank=True, null=True)
    isbn = models.CharField(
        'ISBN', max_length=20,
        blank=True, validators=[RegexValidator(r'^\d+[0-9\-]+[Xx0-9]$')])

    def clean(self):
        if self.isbn:
            try:
                self.isbn = check_isbn(self.isbn)
            except ValueError as e:
                raise ValidationError({'isbn': _(str(e))})

    def __str__(self):
        return '%s ed. of %s' % (self.edition, str(self.book))

    objects = models.Manager()


class Chapter(VitaePublicationModel):
    """Store instance representing book chapter."""

    authors = models.ManyToManyField(
        Collaborator, through='ChapterAuthorship', related_name="chapters")
    editors = models.ManyToManyField(
        Collaborator, through='ChapterEditorship', related_name='editors',
        blank=True)
    # abstract = models.TextField(blank=True)
    book_title = models.CharField(max_length=200)
    volume = models.CharField(max_length=50, null=True, blank=True)
    volumes = models.CharField(
        _("No. of volumes"), max_length=50, null=True, blank=True)
    edition = models.CharField(max_length=50, null=True, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    place = models.CharField(max_length=100, blank=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    series_number = models.CharField(max_length=10, blank=True, null=True)
    start_page = models.CharField(max_length=10, blank=True)
    end_page = models.CharField(max_length=10, blank=True)
    isbn = models.CharField(
        _('ISBN'), max_length=20, blank=True,
        validators=[RegexValidator(r'^\d+[0-9\-]+[Xx0-9]$')])
    url = models.URLField(_('URL'), blank=True)
    grants = models.ManyToManyField(Grant, blank=True)

    abstract_html = models.TextField(blank=True, editable=False)

    objects = models.Manager()


class ChapterAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to article."""

    chapter = models.ForeignKey(
        Chapter, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = (('chapter', 'display_order'))


class ChapterEditorship(CollaborationModel):
    """Store object relating editors to chapter."""

    chapter = models.ForeignKey(
        Chapter, related_name="editorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = (('chapter', 'display_order'))


class Report(VitaePublicationModel):
    """Store instance representing reports."""

    authors = models.ManyToManyField(
        Collaborator, through='ReportAuthorship', related_name="reports")
    # abstract = models.TextField(blank=True)
    report_number = models.CharField(max_length=100, blank=True, null=True)
    report_type = models.CharField(max_length=200, blank=True, null=True)
    series_title = models.CharField(max_length=200, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=100, blank=True, null=True)
    pages = models.CharField(max_length=20, blank=True, null=True)
    url = models.URLField(blank=True)
    doi = models.CharField('DOI', max_length=200, blank=True)

    abstract_html = models.TextField(blank=True, editable=False)

    grants = models.ManyToManyField(Grant, blank=True)

    # def get_primary_files(self):
    #     return self.files.filter(is_primary__exact=True)

    objects = models.Manager()


class ReportAuthorship(CollaborationModel, StudentCollaborationModel):
    """Store object relating collaborators to report."""

    report = models.ForeignKey(
        Report, related_name="authorship", on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_order']
        unique_together = ('report', 'display_order')
