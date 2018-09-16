from markdown import markdown

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from cv.settings import PUBLICATION_STATUS_CHOICES, \
    STUDENT_LEVELS_CHOICES, \
    SERVICE_TYPES_CHOICES, SERVICE_TYPES, \
    FILE_TYPES_CHOICES, \
    TERMS_CHOICES, \
    INPREP_RANGE, INREVISION_RANGE, PUBLISHED_RANGE
from cv.utils import CSLCitation, check_isbn

from .files import CVFile
from .managers import DisplayManager, PublishedManager, ReviseManager, \
    InprepManager


class DisplayableModel(models.Model):  
    """Abstract class including fields shared by all CV models.
    
    :class:`DisplayableModel` makes the ``displayable`` manager available 
    to all models that inherit from it that returns all instances where 
    ``display==True``.  

        display : boolean (required)
        Indicates whether model instance should be displayed and returned by 
        :class:`cv.models.DisplayManager`. Defaults to ``True``.
    
    extra : string
        Text to be included with instance of model. Should be written in final format. 
    
    files : :class:`GenericRelation` to :class:`cv.models.CVFile`
        Relates files to model. 
    
    .. note:: 
      due to rules that Django uses to load managers, it will be defined as the 
      default manager)
    
    """
    display = models.BooleanField(default=True)
    extra = models.TextField(blank=True)
    files = GenericRelation(CVFile)

    displayable = DisplayManager()

    class Meta:
        abstract = True


## Collaborator
class Collaborator(models.Model):
    """
    Store object representing collaborator.
    
    By default, collaborators are ordered (in ascending order) by last name. Internally, 
    Django-CV uses the :attr:`email` attribute to identify collaborators. For example, the 
    template filter :func:`~cv.templatetags.cvtags.print_authors` matches collaborators on 
    e-mails to emphasize key contributors in the list of CV entries based on the list 
    defined in the :setting:`CV_KEY_CONTRIBUTORS_LIST` setting. 
    """
    
    first_name = models.CharField('First (given) name', max_length=100)
    last_name = models.CharField('Last (family) name', max_length=100)
    email = models.EmailField(unique=True)
    middle_initial = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=100,blank=True)
    institution = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    alternate_email = models.EmailField(blank=True)
    
    class Meta:
        ordering = ['last_name']
    
    def __str__(self):
        """String representation of collaborator.

        >>> from cv.models import Collaborator
        >>> info = {"first_name":"Yakko","last_name":"Warner"}
        >>> info.update({"email":"yakko.warner@wbwatertower.com"})
        >>> author = Collaborator.objects.create(**info)
        >>> str(author)
        'Warner, Yakko '
        """
        name = '%s, %s %s' % (
            self.last_name,
            self.first_name,
            self.middle_initial)
        return name.strip()

## Collaboration
class CollaborationModel(models.Model):
    """Abstract model to connect collaborators to products.

        collaborator : :class:`models.ForeignKey` relationship to 
        :class:`Collaborator` Foreign key of collaborator. 

    print_middle : boolean
        Indicates that the collaborator's middle initial should be included.

    display_order : integer (required)
        Order that collaborators should be listed when printed.
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
    """Abstract model to include whether collaborator was a student."""

    student_colleague = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True

## Discipline
class Discipline(models.Model):    
    """
    Store object representing disciplines in which work can be published.
    
    Some models include a Foreign Key relationship to Discipline to allow instances to be
    classified by discipline (e.g., to sort CV by discipline in which articles are 
    published)    
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
        return '%s' % self.name


# C.V. PRODUCTS MODELS
# The following models pertain to knowledge products
# (e.g., grants, articles, books, etc.)
class VitaeModel(DisplayableModel):
    """Create reusable model containing basic titling and discipline fields."""

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
    """
    Create reusable model containing managers for different types
    of publications based on `VitaeModel` fields
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

    published = PublishedManager()
    inprep = InprepManager()
    revise = ReviseManager()

    class Meta:
        abstract = True
        ordering = ['status', '-pub_date', '-submission_date']

    def __str__(self):
        return '%s' % self.short_title

    def save(self, *args, **kwargs):
        self.set_status_fields()
        self.abstract_html = markdown(self.abstract)
        super(VitaePublicationModel, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if getattr(self, 'isbn', ''):
            if self.isbn:
                try:
                    self.isbn = check_isbn(self.isbn)
                except ValueError as e:
                    raise ValidationError({'isbn': _(str(e))})
        super(VitaePublicationModel, self).clean(*args, **kwargs)

    def get_absolute_url(self):
        url_name = 'cv:%s_object_detail' % self._meta.model_name
        return reverse(url_name, kwargs={'slug': self.slug})

    def get_next_previous_by_status(self, direc):
        if direc not in ["previous", "next"]:
            raise SyntaxError("'direc' must be 'previous' or 'next'")
        if (self.status < INREVISION_RANGE.min or
           self.status > PUBLISHED_RANGE.max):
            raise self.DoesNotExist(
                _('%s must be in revision or publication status'
                    % self._meta.object_name))
        sign, db_filter = ("-", "__lt") if direc == "previous" else ("", "__gt")

        # Is it possible to add method to manager to filter by values based
        # on correct date field whether it is the revise or published manager?
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
        mgr = getattr(self.__class__, mgr_name)
        obj = mgr.all().order_by(
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

    def set_status_fields(self):
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

    def cite(self):
        """Return citation based on format defined in CV_CSL_STYLE setting."""
        return CSLCitation(self).cite()


# Journal
class Journal(models.Model):
    """Store object representing journal/periodical in field.

    Three  fields are required: 
    * ``title`` (the title of journal)

    * ``issn`` (the `International Standard Serial Number`_ ,
      written in the format XXXX-XXXX), and

    * ``primary_discipline`` (a Foreign Key to :class:`cv.Discipline`)

    .. _International Standard Serial Number: http://www.issn.org/understanding-the-issn/what-is-an-issn/
    """
    
    title = models.CharField(max_length=200)
    abbreviated_title = models.CharField(
        max_length=100,
        blank=True,
        help_text='Abbreviated journal title; use style you wish to display in views')
    issn = models.CharField(
        'ISSN',
        max_length=9,
        validators=[RegexValidator(r'\d{4}\-\d{3}[0-9X]')],
        help_text='Enter ISSN in format: XXXX-XXXX')
    website = models.URLField(blank=True)
    primary_discipline = models.ForeignKey(
        Discipline,
        related_name='primarydiscipline',
        on_delete=models.CASCADE)
    other_disciplines = models.ManyToManyField(
        Discipline,
        related_name='otherdisciplines',
        blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        """Return string representation of :class:`Journal`"""
        return self.title


        
## C.V. HONORS, AWARDS, AND POSITIONS
# Awards
class Award(DisplayableModel):
    
    """Store object representing an award earned."""
    
    name = models.CharField(max_length=200)
    organization = models.CharField('Granting institution or organization',max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)
    # book = models.ForeignKey(Book,null=True,blank=True,on_delete=models.PROTECT)
    # article = models.ForeignKey(Article,null=True,blank=True,on_delete=models.PROTECT)
    
    class Meta: 
        ordering = ['-date']
        get_latest_by = 'date'
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '%s#award-%s' % (reverse('cv:cv_list'),self.pk)
    
    objects = models.Manager()

## Degrees
class Degree(DisplayableModel):
    
    """Store object representing degree earned.
    
    Degrees are sorted by ``end_date``. 
    
    This class contains two managers:
    * ``objects``: return all positions
    * ``displayable``: return only positions for which ``display==True``
    
    """
    
    degree = models.CharField(max_length=10)
    major = models.CharField(max_length=100,null=True,blank=True)
    date_earned = models.DateField('Date Earned')
    institution = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField('State or Province',max_length=100)
    country = models.CharField(max_length=100)
    honors = models.CharField(max_length=100,null=True,blank=True)
    
    class Meta: 
        ordering = ('-date_earned',)
        get_latest_by = 'date_earned'
        
    def __str__(self):
        return self.degree

    def get_absolute_url(self):
        return '%s#degree-%s' % (reverse('cv:cv_list'),self.pk)

    objects = models.Manager()

## Positions
class PrimaryPositionManager(models.Manager):
    
    """Return positions in which ``primary_position`` has been set to ``True``."""
    
    def get_queryset(self):
        return super(PrimaryPositionManager,self).get_queryset().filter(primary_position=True)

class Position(DisplayableModel):

    """
    Store single position object representing employment or research experience.
    
    Positions are sorted by ``end_date``. 
    
    This class contains three managers:
    * ``objects``: return all positions
    
    * ``displayable``: return only positions for which ``display==True``
    
    * ``primarypositions``: return only positions for which ``primary_position==True``      
      (indicating a primary position should be used sparingly since it will be used, for 
      example, in the heading of a CV)
    
    """
    
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(
        help_text='If current, set date to future (by default positions will be ordered by end date'
        )
    project = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100)
    current_position = models.BooleanField('Current position?',
        help_text='Are you currently in this position?')
    primary_position = models.BooleanField('Primary position?',
        help_text='Should this position be displayed as the main position (e.g., on heading of CV)?'
        )
    
    def clean(self):
        """Ensure start date is before end date."""
        if self.start_date > self.end_date:
            raise ValidationError({'end_date':_('End date cannot be before start date')} )

    def get_absolute_url(self):
        return '%s#position-%s' % (reverse('cv:cv_list'),self.pk)
    
    class Meta:
        ordering = ('-end_date',)
        get_latest_by = 'end_date'
    
    def __str__(self):
        return '%s' % (self.title)
    
    objects = models.Manager()
    primarypositions = PrimaryPositionManager()

        
class MediaMention(DisplayableModel):
    
    """Store object containing media mention."""
    
    ## TODO: Possibly refactor into separate app with generic relations to any model
    outlet = models.CharField(max_length=200,help_text='Publication or station')
    section = models.CharField(max_length=200,
                help_text='Section of publication or program', null=True, blank=True)
    title = models.CharField(max_length=200,null=True,blank=True)
    date = models.DateField()
    url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=200, blank=True, null=True,
                            help_text='E.g., author of written piece or interviewer on visual medium')
    description = models.TextField(blank=True)
    snapshot = models.FileField(null=True,blank=True)
    
    # article = models.ForeignKey(Article,null=True,blank=True,on_delete=models.CASCADE)
    # book = models.ForeignKey(Book,null=True,blank=True,on_delete=models.CASCADE)
    # talk = models.ForeignKey(Talk,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return '%s (%s)' % (self.outlet, self.date.strftime('%b %d, %Y'))
    
    objects = models.Manager()

## SERVICE
## Managers of different levels of service
class DepartmentServiceManager(models.Manager):
    """Return queryset of services perfomed for department."""
    
    def get_queryset(self):
        return super(DepartmentServiceManager, self).get_queryset().filter(
            type__in=[SERVICE_TYPES['DEPARTMENT_SERVICE'],SERVICE_TYPES['SCHOOL_SERVICE']]
            ).filter(
                display=True
            )

class UniversityServiceManager(models.Manager):
    """Return queryset of services perfomed for university."""
    
    def get_queryset(self):
        return super(UniversityServiceManager, self).get_queryset().filter(
                type=SERVICE_TYPES['UNIVERSITY_SERVICE']
            ).filter(
                display=True
            )

class DisciplineServiceManager(models.Manager):
    """Return queryset of services perfomed for university."""
    
    def get_queryset(self):
        return super(DisciplineServiceManager, self).get_queryset().filter(
            type=SERVICE_TYPES['DISCIPLINE_SERVICE']
            ).filter(
                display=True
            )

## Services
class Service(DisplayableModel):
    
    """Add object to record service commitments."""
    
    role = models.CharField(max_length=200)
    group = models.CharField(max_length=200, blank=True, null=True,
        help_text=_('Group or committee on which service was performed'))
    organization = models.CharField(_('Organization or department'),
        max_length=200)
    type = models.IntegerField(choices=SERVICE_TYPES_CHOICES)
    start_date = models.DateField(blank=True,null=True,
        help_text=_("Leave blank of one-time service"))
    end_date = models.DateField(blank=True,null=True,
        help_text=_("Leave blank if service is ongoing"))
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-end_date','-start_date']
    
    def __str__(self):
        return '%s: %s (%s)' % (self.role, self.group, self.organization)
    
    def clean(self):
        check = [self.start_date,self.end_date]
        if not any(check):
            raise ValidationError(_('Must select at least one date field.'))
    
    objects = models.Manager()
    department_services = DepartmentServiceManager()
    university_services = UniversityServiceManager()
    discipline_services = DisciplineServiceManager()

## Reviews
class JournalService(DisplayableModel):
    """Objects representing journals for which one has reviewed."""
    
    journal = models.OneToOneField(Journal,
                    on_delete=models.CASCADE,blank=True,null=True,unique=True)
    is_reviewer = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['journal']
    
    def __str__(self):
        return '%s' % self.journal.title
    
    objects = models.Manager()
    
## Students
class Student(DisplayableModel):
    
    """Add object to represent students that have been advised."""
    
    first_name = models.CharField(max_length=200,null=True)
    last_name = models.CharField(max_length=200,null=True)
    middle_name = models.CharField(max_length=200,null=True,blank=True)
    student_level = models.IntegerField(
        choices=STUDENT_LEVELS_CHOICES,null=True,blank=True
        )
    role = models.CharField(max_length=200,null=True)
    thesis_title = models.CharField(max_length=200,null=True, blank=True)
    is_current_student = models.BooleanField(default=True)
    graduation_date = models.DateField(null=True, blank=True)
    first_position = models.CharField(max_length=200,null=True,blank=True)
    current_position = models.CharField(max_length=200,null=True,blank=True)
    
    class Meta: 
        ordering = ['student_level','graduation_date']
    
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
        _('student level'), choices=STUDENT_LEVELS_CHOICES)

    # Fields used to store html from Markdown input
    short_description_html = models.TextField(editable=False)
    description_html = models.TextField(editable=False)

    last_offered = models.DateField(_('last offered'), null=True)
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
