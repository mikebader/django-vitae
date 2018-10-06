from django.apps import apps
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from sys import modules

from cv.models import Award, Position, Degree, \
    Article, Book, Chapter, Report, \
    Grant, Talk, OtherWriting, Dataset, \
    MediaMention, Service, JournalService, Student, Course
from .pdf import cv_pdf
from .forms import CVCreateView, CVUpdateView, CVDeleteView


MODELS = [Award, Position, Degree,
          Article, Book, Chapter, Report,
          Grant, Talk, OtherWriting, Dataset,
          MediaMention, Service, JournalService,
          Student, Course]


class CVListMixin:
    """Class of helper functions to gather data for CV sections."""

    def sum_items(self, dict):
        """Sum items across dictionaries."""
        return sum([len(i) for i in dict.values()])

    def get_cv_list(self, model):
        """Gather data for CV section into dictionaries."""
        model_name = model._meta.model_name.lower()
        model_plural = model._meta.verbose_name_plural.lower()
        if hasattr(model.displayable, 'management_lists'):
            management_lists = model.displayable.management_lists
            data_dict = dict()
            for mgr in management_lists:
                method = getattr(model.displayable, mgr)
                context_key = '{0}_{1}_list'.format(model_name, mgr)
                data_dict[context_key] = method()
            total_key = 'total_{}'.format(model_plural)
            data_dict[total_key] = self.sum_items(data_dict)
            return data_dict
        return {'{}_list'.format(model_name): model.displayable.all()}

    def get_cv_primary_positions(self):
        """Return dictionary of CV data with current positions."""
        return {'primary_positions': Position.primarypositions.all()}


class CVView(generic.TemplateView, CVListMixin):
    """An HTML representation of a CV."""
    template_name = 'cv/cv.html'

    def get_context_data(self, **kwargs):
        """Return dictionary of different types of CV entries."""
        cv_entry_list = [self.get_cv_list(model) for model in MODELS]
        cv_entry_list += [self.get_cv_primary_positions()]
        context = dict()
        for f in cv_entry_list:
            context.update(f)
        return context


# Views
DETAIL_VIEWS_AVAILABLE = [
    'article', 'book', 'chapter', 'report', 'talk', 'dataset'
]
CITATION_VIEWS_AVAILABLE = DETAIL_VIEWS_AVAILABLE


class CVListView(generic.ListView, CVListMixin):
    """Creates view of all instances for a particular section."""

    def dispatch(self, request, *args, **kwargs):
        """Set class parameters based on URL and dispatch."""
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv', self.model_name)
        self.context_object_name = (
            '%s' % ''.join(self.model._meta.verbose_name_plural))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        mod = modules[__name__]
        return self.get_cv_list(self.model)

    def get_template_names(self):
        """
        Returns the name template to use to display a list of model instances.

        Currently returns ``cv/lists/<model_name>_list.html``.

        Might add a generic template for vitae models in the future.
        """
        return ['cv/lists/%s_list.html' % (self.model_name)]


class CVDetailView(generic.DetailView):
    """Creates view of a single instance of a CV item."""

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        if self.model_name not in DETAIL_VIEWS_AVAILABLE:
            raise Http404('Detailed information not '
                          'available for {0}s'.format(self.model_name))
        self.model = apps.get_model('cv', self.model_name)
        self.context_object_name = (
            '%s' % ''.join(self.model._meta.verbose_name))
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """
        Returns the name template to use to display a list of model instances.

        Currently returns ``cv/lists/<model_name>_detail.html``.

        Might add a generic template for vitae models in the future.
        """
        return ['cv/details/%s_detail.html' % (self.model_name)]


def citation_view(request, model_name, slug, format):
    """Returns view to allow citation to be downloaded to citation management
    software.
    """
    if model_name not in CITATION_VIEWS_AVAILABLE:
        raise Http404('Citation format not '
                      'available for {0}'.format(model_name))
    model = apps.get_model('cv', model_name)
    p = get_object_or_404(model, slug=slug)
    if format == "ris":
        template_file = 'cv/citations/{0}.ris'.format(model_name)
        mime = 'application/x-research-info-systems'
    else:
        template_file = 'cv/citations/{0}.bib'.format(model_name)
        mime = 'application/x-bibtex'
    return render(request, template_file, {model_name: p}, content_type=mime)
