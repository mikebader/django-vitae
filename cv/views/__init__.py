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


# Helper functions to gather data about different parts of CV
def sum_items(dict):
    """Sum items across dictionaries."""
    return sum([len(i) for i in dict.values()])


def get_cv_primary_positions():
    """Return dictionary of CV data with current positions."""
    return {'primary_positions': Position.primarypositions.all()}


def get_cv_personnel_data():
    """Return dictionary of CV data related to personnel and awards."""
    return {
        'award_list': Award.displayable.all(),
        'degree_list': Degree.displayable.all(),
        'position_list': Position.displayable.all()
    }


def get_cv_publication_data(model):
    """Returns dictionary of querysets for publication models."""
    model_name = model._meta.model_name.lower()
    model_plural = model._meta.verbose_name_plural.lower()
    pub_dict = {
        '{0}_published_list'.format(model_name): model.published.all(),
        '{0}_revise_list'.format(model_name): model.revise.all(),
        '{0}_inprep_list'.format(model_name): model.inprep.all(),
    }
    pub_dict['total_{0}'.format(model_plural)] = sum_items(pub_dict)
    return pub_dict


def get_cv_grant_data():
    """Return dictionary of grants."""
    grant_dict = {
        'internal_grants': Grant.internal_grants.all(),
        'external_grants': Grant.external_grants.all()
    }
    grant_dict.update({'total_grants': sum_items(grant_dict)})
    return grant_dict


def get_cv_otherwriting_data():
    """Return dictionary of other writing objects."""
    return {
        'otherwriting_list': OtherWriting.displayable.all()
    }


def get_cv_talk_data():
    """Return dictionary of talks."""
    return {
        'talk_list': Talk.displayable.all()
    }


def get_cv_media_data():
    """Return dictionary of media mentions."""
    return {
        'media_mention_list': MediaMention.displayable.all()
    }


def get_cv_service_data():
    """Return dictionary of services at different levels."""
    service_dict = {
        'department_service_list': Service.department_services.all(),
        'university_service_list': Service.university_services.all(),
        'discipline_service_list': Service.discipline_services.all()
    }
    service_dict['total_service'] = sum_items(service_dict)
    return service_dict


def get_cv_journal_service_data():
    """Return dictionary of journals served."""
    return {
        'journal_service_list': JournalService.objects.all().filter(
            is_reviewer=True
        )
    }


def get_cv_teaching_data():
    """Return dictionary of teaching and mentoring."""
    return {
        'course_list': Course.displayable.all(),
        'student_list': Student.displayable.all()
    }

def get_cv_dataset_data():
    """Return dictionary of datasets."""
    return {
        'dataset_list': Dataset.displayable.all()
    }


def get_cv_data():
    """Return dictionary of different types of CV entries."""
    cv_entry_list = [get_cv_publication_data(model) for model in
                     [Article, Book, Chapter, Report]]
    cv_entry_list += [
        get_cv_primary_positions(), get_cv_personnel_data(),
        get_cv_grant_data(), get_cv_talk_data(), get_cv_otherwriting_data(),
        get_cv_service_data(), get_cv_journal_service_data(),
        get_cv_teaching_data()
    ]
    context = dict()
    for f in cv_entry_list:
        context.update(f)
    return context


# Views
DETAIL_VIEWS_AVAILABLE = [
    'article', 'book', 'chapter', 'report', 'talk', 'dataset'
]
CITATION_VIEWS_AVAILABLE = DETAIL_VIEWS_AVAILABLE


def cv_list(request):
    """Create view of entire CV for printing in `html`."""
    return render(request, 'cv/cv.html', get_cv_data())


class CVListView(generic.ListView):
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
        try:
            queryset_method = getattr(mod, 'get_cv_%s_data' % self.model_name)
            return queryset_method()
        except AttributeError:
            queryset_method = getattr(mod, 'get_cv_publication_data')
            return queryset_method(self.model)

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
