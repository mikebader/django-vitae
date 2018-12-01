from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from copy import copy
from markdown import markdown
import re

from cv.settings import PUBLICATION_STATUS_CHOICES, \
    STUDENT_LEVELS_CHOICES, \
    FILE_TYPES_CHOICES, \
    INPREP_RANGE, INREVISION_RANGE, PUBLISHED_RANGE
from cv.utils import CSLCitation, check_isbn

from .files import CVFile
from .managers import DisplayManager, PublicationManager



class DisplayableModel(models.Model):
    """Abstract class that includes fields shared by all models.

    The abstract class defines three fields common to all models in
    Django-Vitae. The model is managed by
    ``cv.models.managers.DisplayManager``, which is the default manager
    for all models that inherit from DisplayableModel
    """
    display = models.BooleanField(default=True)
    extra = models.TextField(blank=True)
    files = GenericRelation(CVFile)

    displayable = DisplayManager()

    class Meta:
        abstract = True


class Collaborator(models.Model):
    """Representation of collaborator on publications or projects.

    Collaborators represent all people listed in entries of a CV that are
    not the user. Django-Vitae uses the ``email`` attribute to identify
    and manage collaborators internally and must, therefore, be unique
    to each collaborator.

    Collaborators are ordered alphabetically by last name by default.
    """

    first_name = models.CharField('First (given) name', max_length=100)
    last_name = models.CharField('Last (family) name', max_length=100)
    email = models.EmailField(unique=True)
    middle_initial = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    alternate_email = models.EmailField(blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        name = '%s, %s %s' % (
            self.last_name,
            self.first_name,
            self.middle_initial)
        return name.strip()


class CollaborationModel(models.Model):
    """Abstract model connecting collaborators to products.

    Collaborators are tied to the user through specific collaborations. For
    example, a paper with two authors--the user and a 
    collaborator--represents one *collaboration* that has unique 
    characteristics such as the order of authorship. A second paper by the
    same two authors would represent a new collaboration. The abstract
    collaboration model allows for these connections across a variety of
    different collaboration types.

    Fields:

    collaborator : ForeignKey field to the Collaborator model.

    print_middle : Should the collaborator's middle initial be inlcuded in
    the CV entry?

    display_order : Integer representing the order in which
    collaborators are listed. 
    """
    collaborator = models.ForeignKey(Collaborator, on_delete=models.CASCADE)
    print_middle = models.BooleanField(
        default=True,
        help_text='Display author\'s middle initial?')
    display_order = models.IntegerField(
        help_text='Order that collaborators should be listed')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.collaborator)

class StudentCollaborationModel(models.Model):
    """Abstract collaboration model to note collaborations with students.

    Often advisors wish to highlight collaborations with students on CVs.
    This abstract class adds a single field that allows the user to
    indicate whether a collaborator was a student and, if so, the level
    of the student (e.g., undergrad, masters, doctoral).
    """

    student_colleague = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True

## Discipline
class Discipline(models.Model):    
    """Model that represents academic discipline. 
    
    Some models include a Foreign Key relationship to Discipline to allow 
    instances to be classified by discipline (e.g., to sort CV by discipline
    in which articles are published).
    """

    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        """Return string representation of :class:`Discipline`.

        >>> d = Discipline.objects.create(name='Being Zany',slug='being-zany')
        >>> str(d)
        'Being Zany'
        """
        return self.name


class VitaeModel(DisplayableModel):
    """Reusable model containing basic titling and discipline fields."""

    title = models.CharField(max_length=200,
        validators=[RegexValidator(r'\S+')])
    short_title = models.CharField(max_length=80)
    slug = models.SlugField(
        unique=True,
        help_text='Automatically built from short title')
    primary_discipline = models.ForeignKey(
        Discipline,
        related_name='%(app_label)s_%(class)s_primarydiscipline',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    other_disciplines = models.ManyToManyField(
        Discipline,
        related_name='%(app_label)s_%(class)s_otherdisciplines',
        blank=True)

    class Meta:
        abstract = True


class VitaePublicationModel(VitaeModel):
    """Reusable model with fields common to all types of publications.

    The model uses ``cv.models.managers.PublicationManger`` to manage instances
    of the model. The ``PublicationManager`` is named ``displayable``.

    Internally managed fields: ``VitaePublicationModel`` instances
    include three fields managed internally related to publication
    status: ``is_published``, ``is_inrevision``, and ``is_inprep``.
    The values of each of these boolean fields are set when cleaning the
    model instance. Django-Vitae also manages an ``abstract_html`` field
    internally to save an HTML version of markdown text saved in the
    ``abstract`` field.

    Custom methods:

    ``get_next_by_status()`` and ``get_previous_by_status`` mimic Django's
    built-in methods ``get_next_by()`` and ``get_previous_by`` but inlcudes
    a constraint that the publication status must be the same as that of
    the current model instance.

    ``cite()`` prints the instance's citation using the CSL format defined
    in the ``CV_CITE_CSL_STYLE`` setting.

    """
    abstract = models.TextField(blank=True)
    status = models.IntegerField(
        choices=PUBLICATION_STATUS_CHOICES)
    pub_date = models.DateField(
        'Publication date',
        blank=True,
        null=True)
    submission_date = models.DateField(
        blank=True,
        null=True)

    is_published = models.BooleanField(default=False, editable=False)
    is_inrevision = models.BooleanField(default=False, editable=False)
    is_inprep = models.BooleanField(default=False, editable=False)

    abstract_html = models.TextField(blank=True, editable=False)

    displayable = PublicationManager()

    class Meta:
        abstract = True
        ordering = ['status', '-pub_date', '-submission_date']

    def __str__(self):
        return '%s' % self.short_title

    def save(self, *args, **kwargs):
        """Sets publication status booleans and abstract text in HTML."""
        self._set_status_fields()
        self.abstract_html = markdown(self.abstract)
        super(VitaePublicationModel, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Checks ISBN validity."""
        if getattr(self, 'isbn', ''):
            if self.isbn:
                try:
                    self.isbn = check_isbn(self.isbn)
                except ValueError as e:
                    raise ValidationError({'isbn': _(str(e))})
        super(VitaePublicationModel, self).clean(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'cv:item_detail',
            kwargs={'model_name': self._meta.model_name, 'slug': self.slug}
        )

    def _set_status_fields(self):
        """Sets boolean values for each of three publication statuses."""
        for status in ['is_published', 'is_inrevision', 'is_inprep']:
            setattr(self, status, False)
        if (self.status and
           PUBLISHED_RANGE.min <= self.status < PUBLISHED_RANGE.max):
                self.is_published = True
        if (self.status and
           INREVISION_RANGE.min <= self.status < INREVISION_RANGE.max):
                self.is_inrevision = True
        if (self.status is not None and
           INPREP_RANGE.min <= self.status < INPREP_RANGE.max):
                self.is_inprep = True

    def get_next_previous_by_status(self, direc):
        """Retrieves next or previous instance with same publication status."""
        if direc not in ["previous", "next"]:
            raise SyntaxError("'direc' must be 'previous' or 'next'")
        if (self.status < INREVISION_RANGE.min or
           self.status > PUBLISHED_RANGE.max):
            raise self.DoesNotExist(
                _('%s must be in revision or publication status'
                    % self._meta.object_name))
        sign, db_filter = ("-", "__lt") if direc == "previous" else ("", "__gt")

        if self.status < PUBLISHED_RANGE.min:
            mgr_name, filter_var = ("revise", "submission_date")
        else:
            mgr_name, filter_var = ("published", "pub_date")
        ref_date = getattr(self, filter_var)
        if ref_date is None:
            raise ValueError('%s instance must have %s to get %s publication '
                             'by status' %
                             (self._meta.object_name, filter_var, direc))
        filter_params = {filter_var + db_filter: ref_date}
        mgr = getattr(self.__class__.displayable, mgr_name)
        obj = mgr().order_by(
            '%s%s' % (sign, filter_var)).filter(**filter_params).first()
        if obj:
            return obj
        direc = "subsequent" if direc == "next" else direc
        raise self.DoesNotExist(
            _("There are no %s %ss with same status.")
            % (direc, self._meta.object_name))

    def get_previous_by_status(self):
        return self.get_next_previous_by_status("previous")

    def get_next_by_status(self):
        return self.get_next_previous_by_status("next")

    def get_primary_files(self):
        """Return queryset of :class:`cv.models.CVFile` objects designated
        as "primary files" associated with article."""
        return self.files.filter(is_primary__exact=True)

    def cite(self, style='html', doi=True):
        """Return citation of instance.

        The format used for the citation is set using the
        CV_CITE_CSL_STYLE setting.
        """
        if style not in ['html', 'plain']:
            raise ValueError(('Citation style must be either \'html\' or'
                              ' \'plain\''))
        if style == 'html':
            return CSLCitation(self).cite_html(doi=doi)
        return CSLCitation(self).cite_plain(doi=doi)


# Journal
class Journal(models.Model):
    """Store object representing journal/periodical in field.

    The model contains one internally managed field, ``title_no_article``,
    which stores the name of the title without the leading articles
    'A', 'An' or 'The'. The field is used to alphabetize journals by
    titles without the leading article, `per APA style`_.

    .. _per APA style: https://blog.apastyle.org/apastyle/2010/05/alphabetization-in-apa-style.html 


    The model includes an ``issn`` field that stores the
    `International Standard Serial Number`_  for the journal. Future
    versions might require the issn field to prevent duplicate journal
    entries and to allow automatic updating of journal lists.

    .. _International Standard Serial Number: http://www.issn.org/understanding-the-issn/what-is-an-issn/
    """

    title = models.CharField(max_length=200, unique=True)
    abbreviated_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Abbreviated journal title; '
                    'use style you wish to display in views'))
    issn = models.CharField(
        'ISSN',
        max_length=9,
        validators=[RegexValidator(r'\d{4}\-\d{3}[0-9X]')],
        help_text='Enter ISSN in format: XXXX-XXXX',
        blank=True)
    website = models.URLField(blank=True)
    primary_discipline = models.ForeignKey(
        Discipline,
        related_name='primarydiscipline',
        on_delete=models.CASCADE,
        null=True, blank=True)
    other_disciplines = models.ManyToManyField(
        Discipline,
        related_name='otherdisciplines',
        blank=True)

    title_no_article = models.CharField(
        max_length=200, blank=True, editable=False)

    class Meta:
        ordering = ['title_no_article']

    def __str__(self):
        """Return string representation of :class:`Journal`"""
        return self.title

    def save(self, *args, **kwargs):
        self.title_no_article = re.sub(
            '^An |^A |^The |^a |^an |^the ', '', self.title).strip()
        super(Journal, self).save(*args, **kwargs)



# class MediaMention(DisplayableModel):
#     """Mention in media outlet."""

#     # TODO: Possibly refactor into separate app with generic relations
#     #       to any model
#     outlet = models.CharField(
#         max_length=200, help_text=_('Publication or station'))
#     section = models.CharField(
#         max_length=200, null=True, blank=True,
#         help_text=_('Section of publication or program'))
#     title = models.CharField(max_length=200, null=True, blank=True)
#     date = models.DateField()
#     url = models.URLField(blank=True, null=True)
#     author = models.CharField(
#         max_length=200, blank=True, null=True,
#         help_text=_('E.g., author of written piece or interviewer on '
#                     'visual medium'))
#     description = models.TextField(blank=True)
#     snapshot = models.FileField(null=True, blank=True)

#     # article = models.ForeignKey(Article,null=True,blank=True,on_delete=models.CASCADE)
#     # book = models.ForeignKey(Book,null=True,blank=True,on_delete=models.CASCADE)
#     # talk = models.ForeignKey(Talk,null=True,blank=True,on_delete=models.CASCADE)

#     class Meta:
#         ordering = ['-date']

#     def __str__(self):
#         return '%s (%s)' % (self.outlet, self.date.strftime('%b %d, %Y'))

#     objects = models.Manager()
        
