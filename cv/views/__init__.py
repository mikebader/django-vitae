from django.apps import apps
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from cv.models import Award, Position, Degree, \
    Article, Book, Chapter, Report, \
    Grant, Talk, OtherWriting, Dataset, \
    Service, JournalService, Student, Course
from cv.settings import CITATION_DOWNLOAD_FORMATS as fmts
from cv.settings import DETAIL_VIEWS_AVAILABLE, CITATION_VIEWS_AVAILABLE

from .pdf import cv_pdf
from .forms import CVCreateView, CVUpdateView, CVDeleteView


MODELS = [Award, Position, Degree,
          Article, Book, Chapter, Report,
          Grant, Talk, OtherWriting, Dataset,
          Service, JournalService,
          Student, Course]


class CVListMixin:
    """Class of helper functions to gather data for CV sections."""

    def _sum_items(self, d):
        """Sum items across dictionaries.

        :param d: Dictionary containing dictionary as values
        :type d: dict
        """
        return sum([len(i) for i in d.values()])

    def _get_cv_primary_positions(self):
        """Return dictionary of CV data with current positions."""
        return {'primary_positions': Position.primary_positions.all()}

    def get_cv_list(self, model):
        """Gather data for CV section into dictionaries.

        :param model: A model class
        :type model: :mod:`cv.model` class

        Creates a dictionary lookup with a single key for items in a
        model class that CV views use to display data. The key will always be
        ``<model>_list`` where ``<model>`` is a lowercase string of the model
        class (e.g., the key for :class:`~cv.models.Article` is
        ``article_list``).

        If the model class has only a single manager, the value for the
        dictionary entry is a :class:`~django.db.models.query.QuerySet` of all
        objects retruned by the ``displayable`` manager.

        If the model class has multiple managers, the value for the dictionary
        entry with the key ``model_list`` is itself a dictionary where the
        keys are ``<manager>`` and the values are a
        :class:`~django.db.models.query.QuerySet` of all objects returned
        by the manager and a final entry with key ``total`` that has as its
        value the total number of objects returned across the different
        managers. For example::

            >> from cv.models import Article
            >> from cv.views.CVListMixin import get_cv_list
            >> from cv.settings import PUBLICATION_STATUS
            >>
            >> pub = Article.objects.create(
            >>    title='Published Article', short_title='Published',
            >>    slug='published', status=PUBLICATION_STATUS['PUBLISHED_STATUS'])
            >> rev = Article.objects.create(
            >>    title='Revision Article', short_title='Revision',
            >>    slug='revision', status=PUBLICATION_STATUS['REVISE_STATUS'])
            >> prp = Article.objects.create(
            >>    title='In Prep Article', short_title='In Prep',
            >>    slug='inprep', status=PUBLICATION_STATUS['INPREP_STATUS'])
            >> get_cv_list(Article)
            {'article_list': {'inprep': <QuerySet [<Article: In Prep>]>,
                  'published': <QuerySet [<Article: Published>]>,
                  'revise': <QuerySet [<Article: Revision>]>,
                  'total': 3}}
        """
        model_name = model._meta.model_name.lower()
        list_name = '{}_list'.format(model_name)
        if hasattr(model.displayable, 'management_lists'):
            management_lists = model.displayable.management_lists
            data_dict = {}
            for mgr in management_lists:
                method = getattr(model.displayable, mgr)
                context_key = '{}'.format(mgr)
                data_dict[context_key] = method()
            data_dict['total'] = self._sum_items(data_dict)
            return {list_name: data_dict}
        return {list_name: model.displayable.all()}


class CVView(generic.TemplateView, CVListMixin):
    """Representation of an entire CV."""
    template_name = 'cv/cv.html'

    def get_context_data(self, **kwargs):
        """Construct data to render entire CV.

        Creates context as a dictionary with keys constructed as
        ``<model>_list`` for each model class and values being the
        data returned by :meth:`cv.views.CVListMixin.get_cv_list` method
        for each model class.
        """
        cv_entry_list = [self.get_cv_list(model) for model in MODELS]
        cv_entry_list += [self._get_cv_primary_positions()]
        context = dict()
        for f in cv_entry_list:
            context.update(f)
        return context


class CVListView(generic.ListView, CVListMixin):
    """Creates view of all instances for a particular section."""

    def setup(self, request, *args, **kwargs):
        """Add model class and string of model name to view."""
        super(CVListView, self).setup(request, *args, **kwargs)
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv', self.model_name)

    def get_context_data(self, **kwargs):
        """Add model and section information to the context."""
        context = super(CVListView, self).get_context_data(**kwargs)
        model_name = self.model._meta.verbose_name
        context['model_name'] = model_name
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['section_template'] = 'cv/sections/{}.html'.format(model_name)
        return context

    def get_queryset(self):
        """Construct list of items to render in section list view.

        Returns a dictionary created using
        :meth:`cv.views.CVListMixin.get_cv_list` based on model class.
        """
        return self.get_cv_list(self.model)['{}_list'.format(self.model_name)]

    def get_template_names(self):
        """
        Template names returned for the CV list view.

        Will use ``cv/lists/<model>.html`` template if it exists, otherwise
        will default to ``cv/lists/cv_list.html``.
        """
        return ['cv/lists/{}.html'.format(self.model_name),
                'cv/lists/cv_list.html']


class CVDetailView(generic.DetailView):
    """Creates view of a single instance of a CV item."""

    def setup(self, request, *args, **kwargs):
        """Add attributes to view if model is in approved list.

        Checks whether the class model is on included in the setting
        :setting:`DETAIL_VIEWS_AVAILABLE` and, if so, adds attributes
        to the view, including ``context_object_name`` that will be set
        to the verbose name of the model class.
        """
        self.model_name = kwargs['model_name']
        if self.model_name not in DETAIL_VIEWS_AVAILABLE:
            raise Http404('Detailed information not '
                      'available for {}s'.format(self.model_name))
        super(CVDetailView, self).setup(request, *args, **kwargs)
        self.model = apps.get_model('cv', self.model_name)
        self.context_object_name = '{}'.format(
            self.model._meta.verbose_name)

    def get_context_data(self, **kwargs):
        """Add model and section information to the context."""
        context = super(CVDetailView, self).get_context_data(**kwargs)
        context['model_name'] = type(context['object']).__name__.lower()
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        return context

    def get_template_names(self):
        """
        Template names returned for the CV detail view.

        Will use ``cv/details/<model>.html`` template if it exists, otherwise
        will default to ``cv/details/cv_detail.html``.
        """
        return ['cv/details/{}.html'.format(self.model_name),
                'cv/details/cv_detail.html']


def citation_view(request, model_name, slug, fmt):
    """View to download citation into to citation management software.

    :param model_name: lowercase name of model type
    :param slug: slug of object for the citation
    :param fmt: format of the citation download

    This view allows users to download the citation for an instance of a model
    into citation management software such as Zotero_ or BibTeX_. Bases
    available download formats on
    :setting:`CITATION_DOWNLOAD_FORMATS` and models with
    downloadable citation views based on
    :setting:`CITATION_VIEWS_AVAILABLE`.

    .. _Zotero: https://www.zotero.org/
    .. _BibTex: http://www.bibtex.org/Format/

    """
    if model_name not in CITATION_VIEWS_AVAILABLE:
        raise Http404('Citation downloads not '
                      'available for {0}'.format(model_name))
    model = apps.get_model('cv', model_name)
    p = get_object_or_404(model, slug=slug)
    try:
        mime = fmts[fmt]
    except KeyError:
        raise Http404('Citation format {} not available'.format(fmt))
    template_file = 'cv/citations/{}.{}'.format(model_name, fmt)
    return render(
        request, template_file, {model_name: p}, content_type=mime)
    
