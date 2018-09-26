from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from sys import modules

from .models import Award, Position, Degree, \
    Article, Book, Chapter, Report, \
    Grant, Talk, OtherWriting, \
    MediaMention, Service, JournalService, Student


## Helper functions to gather data about different parts of CV
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

def get_cv_service_data():
    """Return dictionary of services at different levels."""
    service_dict = {
        'department_service_list' : Service.department_services.all(),
        'university_service_list' : Service.university_services.all(),
        'discipline_service_list' : Service.discipline_services.all()
        }
    service_dict['total_service']=sum_items(service_dict)
    return service_dict

def get_cv_journal_service_data():
    """Return dictionary of journals served."""
    return {
        'journal_service_list' : JournalService.objects.all().filter(is_reviewer=True)
        }

def get_cv_article_data():
    """Return dictionary of articles in different stages of publication."""
    article_dict = {
        'article_published_list': Article.published.all(),
        'article_revise_list': Article.revise.all(),
        'article_inprep_list': Article.inprep.all()
        }
    article_dict['total_articles']=sum_items(article_dict)
    return article_dict

def get_cv_chapter_data():
    """Return dictionary of chapters in different stages of publication."""
    chapter_dict = {
        'chapter_published_list': Chapter.published.all(),
        'chapter_revise_list': Chapter.revise.all(),
        'chapter_inprep_list': Chapter.inprep.all()
        }
    chapter_dict['total_chapters']=sum_items(chapter_dict)
    return chapter_dict

def get_cv_book_data():
    """Return dictionary of books in different stages of publication."""
    book_dict = {
        'book_published_list': Book.published.all(),
        'book_revise_list': Book.revise.all(),
        'book_inprep_list': Book.inprep.all()
        }
    book_dict['total_books']=sum_items(book_dict)
    return book_dict

def get_cv_grant_data():
    """Return dictionary of grants."""
    grant_dict = {
        'internal_grants': Grant.internal_grants.all(),
        'external_grants': Grant.external_grants.all()
        }
    grant_dict.update({'total_grants':sum_items(grant_dict)})
    return grant_dict

def get_cv_report_data():
    """Return dictionary of reports in different stages of publication."""
    report_dict = {
        'report_published_list': Report.published.all(),
        'report_revise_list': Report.revise.all(),
        'report_inprep_list': Report.inprep.all()
        }
    report_dict['total_reports']=sum_items(report_dict)
    return report_dict

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

def get_cv_teaching_data():
    """Return dictionary of teaching and mentoring."""
    context = {'student_list': Student.displayable.all()}
    try:
        from courses.models import Course
        context.update({'course_list': Course.displayable.all()})
        return context
    # except ImportError:
    except:
        return context

def get_cv_data():
    """Return dictionary of different types of CV entries."""
    cv_entry_list = [
        get_cv_primary_positions(), get_cv_personnel_data(), get_cv_service_data(), 
        get_cv_journal_service_data(), get_cv_article_data(), get_cv_chapter_data(), 
        get_cv_book_data(), get_cv_talk_data(), get_cv_otherwriting_data(),
        get_cv_media_data(), get_cv_teaching_data(), get_cv_grant_data()
        ]
    context = dict()
    for f in cv_entry_list:
        context.update(f)
    return context


# Views
DETAIL_VIEWS_AVAILABLE = [
    'article', 'book', 'chapter', 'report', 'talk'
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
        queryset_method = getattr(mod, 'get_cv_%s_data' % self.model_name)
        return queryset_method()

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
from django.views.generic.edit import CreateView, UpdateView, DeleteView, SingleObjectTemplateResponseMixin
from django.urls import reverse_lazy
from django.apps import apps
from .forms import authorship_formset_factory, \
                   edition_formset_factory, \
                   editorship_formset_factory, \
                   grant_collaboration_formset_factory, \
                   presentation_formset_factory

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

    def get_context_data(self, **kwargs):
        """
        Set common context variables for CV views and set value of
        authorship formset

        ``self.formset`` will be:
        * ``inlineformset_factory`` for the authorship model if one exists
        * ``None`` otherwise
        """
        context = super(CVSingleObjectMixin, self).get_context_data(**kwargs)
        context['method'] = self.method.title()
        context['model'] = self.model_name
        self.authorship_formset = authorship_formset_factory(self.model_name)
        self.edition_formset = None
        if self.model_name=='book':
            self.edition_formset = edition_formset_factory()
        self.editorship_formset = None
        if self.model_name=='chapter':
            self.editorship_formset = editorship_formset_factory()
        self.grant_collaboration_formset = None
        if self.model_name=='grant':
            self.grant_collaboration_formset = grant_collaboration_formset_factory()
        self.presentation_formset = None
        if self.model_name=='talk':
            self.presentation_formset = presentation_formset_factory()
        self.formsets = list()
        for formset in ['authorship', 'edition', 'editorship',
                        'grant_collaboration', 'presentation']:
            formset_name = '{0}_formset'.format(formset)
            if getattr(self, formset_name):
                self.formsets.append(formset_name)
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
        self.formsets = list()
        for formset_name in self.formsets:
            make_formset = getattr(self, formset_name)
            if make_formset:
                self.formsets.append(formset_name)
                if self.request.POST:
                    context[formset_name] = make_formset(self.request.POST)
                else:
                    context[formset_name] = make_formset()

        context['action_url'] = reverse_lazy(
            'cv:cv_add',
            kwargs={'model_name': self.model_name}
        )
        return context

    def form_valid(self, form):
        """Save authorship formset data if valid."""
        context = self.get_context_data()
        for formset_name in self.formsets:
            formset = context[formset_name]
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            else:
                return self.render_to_response(
                    self.get_context_data(form=form))
        super().form_valid(form)
        return redirect(self.success_url)


class CVUpdateView(UpdateView, CVSingleObjectMixin):
    """View to edit CV objects."""

    method = 'edit'
    template_name = "cv/forms/cv_edit_form.html"
    success_url = reverse_lazy('cv:cv_list')

    def get_context_data(self, **kwargs):
        context = super(CVUpdateView, self).get_context_data(**kwargs)
        for formset in ['authorship', 'edition', 'editorship',
                        'grant_collaboration']:
            formset_name = '{0}_formset'.format(formset)
            make_formset = getattr(self, formset_name)
            if make_formset:
                if self.request.POST:
                    context[formset_name] = make_formset(
                        self.request.POST,
                        instance=self.object)
                else:
                    context[formset_name] = make_formset(
                        instance=self.object)
        context['model'] = self.model_name
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

    def form_valid(self, form):
        """Save authorship formset data if valid."""
        context = self.get_context_data()
        formsets = self.formsets
        for formset_name in self.formsets:
            formset = context[formset_name]
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            else:
                return self.render_to_response(
                    self.get_context_data(form=form))
        super().form_valid(form)
        return redirect(self.success_url)

class CVDeleteView(DeleteView):
    success_url = reverse_lazy('cv:cv_list')
    template_name = 'cv/forms/cv_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv',self.model_name)
        return super().dispatch(request, *args, **kwargs)
