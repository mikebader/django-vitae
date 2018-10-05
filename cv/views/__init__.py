from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from sys import modules

from cv.models import Award, Position, Degree, \
    Article, Book, Chapter, Report, \
    Grant, Talk, OtherWriting, Dataset, \
    MediaMention, Service, JournalService, Student, Course


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


# Forms
from django.db import transaction
from django.views.generic.edit import CreateView, UpdateView, DeleteView, SingleObjectTemplateResponseMixin
from django.urls import reverse_lazy
from django.apps import apps
from cv.forms import authorship_formset_factory, \
                   edition_formset_factory, \
                   editorship_formset_factory, \
                   grant_collaboration_formset_factory, \
                   presentation_formset_factory, \
                   offering_formset_factory

def template_name(model_name, suffix):
#   model_name = model.__name__.lower()
    return "cv/forms/%s%s.html" % (model_name,suffix)


fieldsets = {
    'award': ['name', 'organization', 'date', 'description'],
    'degree': ['degree', 'major', 'date_earned', 'institution', 'city',
               'state', 'country', 'honors'],
    'position': ['title', 'start_date', 'end_date', 'project',
                 'department', 'institution', 'current_position',
                 'primary_position'],
    'article': ['title', 'status', 'display', 'submission_date', 'pub_date',
                'short_title', 'slug', 'abstract', 'journal', 'volume',
                'issue', 'start_page', 'end_page', 'url', 'series',
                'number', 'doi', 'pmcid', 'pmid', 'grants',
                'primary_discipline', 'other_disciplines', 'extra'],
    'book': ['title', 'short_title', 'slug', 'status', 'display',
             'submission_date', 'pub_date', 'abstract', 'publisher',
             'place', 'volume', 'series', 'series_number', 'num_pages',
             'isbn', 'url', 'grants', 'primary_discipline',
             'other_disciplines', 'extra'],
    'chapter': ['title', 'short_title', 'slug', 'status', 'display',
                'submission_date', 'pub_date', 'abstract', 'book_title',
                'volume', 'volumes', 'edition', 'publisher', 'place',
                'series', 'series_number', 'start_page', 'end_page',
                'isbn', 'url', 'grants', 'primary_discipline',
                'other_disciplines'],
    'report': ['title', 'short_title', 'slug', 'status', 'display',
               'submission_date', 'pub_date', 'abstract', 'report_number',
               'report_type', 'series_title', 'place', 'institution',
               'pages', 'url', 'doi', 'grants', 'primary_discipline',
               'other_disciplines'],
    'grant': ['title', 'short_title', 'slug', 'display', 'source', 'role',
              'agency', 'agency_acronym', 'division', 'division_acronym',
              'grant_number', 'amount', 'start_date', 'end_date',
              'is_current', 'abstract', 'primary_discipline',
              'other_disciplines'],
    'otherwriting': ['title', 'short_title', 'slug', 'type', 'venue', 'date',
                     'pages', 'url', 'place', 'volume', 'issue', 'abstract'],
    'talk': ['title', 'short_title', 'slug', 'display', 'abstract','grants',
             'primary_discipline', 'other_disciplines'],
    'service': ['role', 'group', 'organization', 'type', 'start_date',
                'end_date', 'description'],
    'student': ['first_name', 'last_name', 'middle_name', 'student_level',
                'role', 'thesis_title', 'is_current_student',
                'graduation_date', 'first_position', 'current_position'],
    'course': ['title', 'slug', 'short_description', 'full_description', 
               'student_level']
}


class CVSingleObjectMixin(SingleObjectTemplateResponseMixin):
    """
    Provide basic methods for manipulating CV views.
    """
    def dispatch(self, request, *args, **kwargs):
        """Set class parameters and dispatch to right method."""
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv', self.model_name)
        self.fields = fieldsets[self.model_name]
        return super().dispatch(request, *args, **kwargs)

    def get_formset_factories(self):
        """Return a dictionary of formset names and factory methods."""
        factories = dict()
        authorship_formset = authorship_formset_factory(self.model_name)
        if authorship_formset:
            factories['authorship_formset'] = authorship_formset
        if self.model_name=='book':
            factories['edition_formset'] = edition_formset_factory()
        if self.model_name=='chapter':
            factories['editorship_formset'] = editorship_formset_factory()
        if self.model_name=='grant':
            factories['grant_collaboration_formset'] = grant_collaboration_formset_factory()
        if self.model_name=='talk':
            factories['presentation_formset'] = presentation_formset_factory()
        if self.model_name=='course':
            factories['offering_formset'] = offering_formset_factory()
        return factories

    def get_context_data(self, **kwargs):
        """Set common context variables for CV views and get formset factories.
        """
        context = super(CVSingleObjectMixin, self).get_context_data(**kwargs)
        context['method'] = self.method.title()
        context['model'] = self.model_name
        self.factories = self.get_formset_factories()

        return context

    def get_template_names(self):
        """
        Return a list of template names to be used for the form to create
        a new object. Returns either:
        * ``cv/forms/<model_name>_add_form.html`` or
        * the ``template_name`` defined for the view
        """
        return ['cv/forms/%s.html' % (self.model_name),
                self.template_name,
                'cv/forms/cv_%s_form.html' % (self.method)]


class CVCreateView(CreateView, CVSingleObjectMixin):
    """View to create CV objects """

    method = 'add'
    template_name = "cv/forms/cv_add_form.html"
    success_url = reverse_lazy('cv:cv_list')

    def get_context_data(self, **kwargs):
        """Insert authorship formset into the context dict."""
        context = super(CVCreateView, self).get_context_data(**kwargs)
        context['model'] = self.model_name
        for name, factory in self.factories.items():
            if self.request.POST:
                context[name] = factory(self.request.POST)
            else:
                context[name] = factory()
        context['action_url'] = reverse_lazy(
            'cv:cv_add',
            kwargs={'model_name': self.model_name}
        )
        return context

    def check_formsets_valid(self, formsets):
        return all(formset.is_valid() is True for formset in formsets)

    def form_valid(self, form):
        context = self.get_context_data()
        formsets = [context[factory] for factory in self.factories]
        if self.check_formsets_valid(formsets):
            self.object = form.save()
            for formset in formsets:
                formset.instance = self.object
                formset.save()
            return super(CVCreateView, self).form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    # def form_valid(self, form):
    #     """Save authorship formset data if valid."""
    #     context = self.get_context_data()
    #     for factory in self.factories:
    #         formset = context[factory]
    #         if formset.is_valid():
    #             self.object = form.save()
    #             formset.instance = self.object
    #             formset.save()
    #         else:
    #             return self.render_to_response(
    #                 self.get_context_data(form=form))
    #     return super().form_valid(form)


class ReportUpdateView(UpdateView):
    model = Report
    fields = fieldsets['report']
    template_name = 'cv/forms/report.html'
    success_url = reverse_lazy('cv:cv_list')

    def get_context_data(self, **kwargs):
        context = super(ReportUpdateView, self).get_context_data(**kwargs)
        authorship_factory = authorship_formset_factory('report')
        if self.request.POST:
            context['authorship_formset'] = authorship_factory(
                self.request.POST, instance=self.object)
        else:
            context['authorship_formset'] = authorship_factory(
                instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        authorship = context['authorship_formset']
        self.object = form.save()

        if authorship.is_valid():
            print("Authorship True")
            authorship.instance = self.object
            authorship.save()
        else:
            print("Authorship False")
            print(authorship.errors)
            return self.render_to_response(self.get_context_data(form=form))

        return super(ReportUpdateView, self).form_valid(form)

class CVUpdateView(UpdateView, CVSingleObjectMixin):
    """View to edit CV objects."""

    method = 'edit'
    template_name = "cv/forms/cv_edit_form.html"
    success_url = reverse_lazy('cv:cv_list')

    def get_context_data(self, **kwargs):
        context = super(CVUpdateView, self).get_context_data(**kwargs)
        context['model'] = self.model_name
        for name, factory in self.factories.items():
            if self.request.POST:
                context[name] = factory(
                    self.request.POST, instance=self.object)
            else:
                context[name] = factory(instance=self.object)
        context['action_url'] = reverse_lazy(
            'cv:cv_edit',
            kwargs={'pk': context['object'].id,
                    'model_name': self.model_name}
        )
        context['delete_url'] = reverse_lazy(
            'cv:cv_delete',
            kwargs={'pk': context['object'].id,
                    'model_name': self.model_name}
        )        
        return context

    def check_formsets_valid(self, formsets):
        return all(formset.is_valid() is True for formset in formsets)

    def form_valid(self, form):
        context = self.get_context_data()
        formsets = [context[factory] for factory in self.factories]
        if self.check_formsets_valid(formsets):
            self.object = form.save()
            for formset in formsets:
                formset.instance = self.object
                formset.save()
            return super(CVUpdateView, self).form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

class CVDeleteView(DeleteView):
    success_url = reverse_lazy('cv:cv_list')
    template_name = 'cv/forms/cv_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv',self.model_name)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CVDeleteView, self).get_context_data(**kwargs)
        context['model'] = self.model_name
        return context

import io
from django.http import FileResponse, HttpResponse
from cv.views.pdf import CVPdf

def cv_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="cv.pdf"'
    buffer = io.BytesIO()
    pdf = CVPdf()
    pdf_out = pdf.build_cv(buffer)
    response.write(pdf_out)
    return response
