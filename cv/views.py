from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader, Context, RequestContext
from django.views import generic

from .models import Collaborator, Journal, Discipline, Award, \
                    Position, Degree, \
                    Grant, GrantCollaboration, \
                    Article, ArticleAuthorship, \
                    Chapter, ChapterAuthorship,\
                    Book, BookAuthorship, BookEdition, \
                    Report, ReportAuthorship, \
                    Talk, Presentation, OtherWriting, \
                    MediaMention, Service, JournalService, Student 

#from .forms import DegreeForm, AwardForm

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

## Views
def cv_list(request):   
    """Create view of entire CV for printing in `html`."""
    return render(request, 'cv/cv.html', get_cv_data())

class ArticleListView(generic.ListView):
    
    """Return list of articles"""
    
    template_name = 'cv/lists/article_list.html'
    context_object_name = 'article_objects'
    
    def get_queryset(self):
        return get_cv_article_data()
            
class ArticleDetailView(generic.DetailView):
    
    """Return view of a single article"""
    
    model = Article
    template_name = 'cv/details/article_detail.html'
    context_object_name = 'article' 

def article_citation_view(request,slug,format):
    """Returns view to allow citation to be downloaded to citation management 
    software."""
    p = get_object_or_404(Article,slug=slug)
    if format=="ris":
        template_file = 'cv/citations/article.ris'
        mime='application/x-research-info-systems'
    else:
        template_file = 'cv/citations/article.bib'
        mime='application/x-bibtex'
    return render(request, template_file, {'article':p},content_type=mime)

class BookListView(generic.ListView):
    
    """Return list of books"""

    template_name = 'cv/lists/book_list.html'
    context_object_name = 'book_objects'

    def get_queryset(self):
        return get_cv_book_data()

class BookDetailView(generic.DetailView):

    """Return view of single book"""

    model = Book
    template_name = 'cv/details/book_detail.html'
    context_object_name = 'book'

def book_citation_view(request, slug, format):
    """Returns view to allow citation to be downloaded to citation management
    software in RIS or BibTeX formats."""
    p = get_object_or_404(Book, slug=slug)
    if format == "ris":
        template_file = 'cv/citations/book.ris'
        mime = 'application/x-research-info-systems'
    else:
        template_file = 'cv/citations/book.bib'
        mime = 'application/x-bibtex'
    return render(request, template_file, {'book':p}, content_type=mime)

class ChapterListView(generic.ListView):
    """Return view containing list of chapters."""
    template_name = 'cv/lists/chapter_list.html'
    context_object_name = 'chapter_objects'

    def get_queryset(self):
        return get_cv_chapter_data()

class ChapterDetailView(generic.DetailView):
    """Return view containing details of single chapter."""
    model = Chapter
    template_name = 'cv/details/chapter_detail.html'
    context_object_name = 'chapter'


def chapter_citation_view(request, slug, format):
    """Returns citation to be downloaded to citation management software."""
    p = get_object_or_404(Chapter, slug=slug)
    if format == "ris":
        template_file = 'cv/citations/chapter.ris'
        mime = 'application/x-research-info-systems'
    else:
        template_file = 'cv/citations/chapter.bib'
        mime = 'application/x-bibtex'
    return render(request, template_file, {'report': p}, content_type=mime)


class ReportListView(generic.ListView):
    """
    Return view containing list of reports.
    
    """
    
    template_name = 'cv/lists/report_list.html'
    context_object_name = 'report_objects'
    
    def get_queryset(self):
        return get_cv_report_data()
    
class ReportDetailView(generic.DetailView):
    """
    Return view containing details of single report.
    
    """
    
    model = Report
    template_name = 'cv/details/report_detail.html'
    context_object_name = 'report'
    
def report_citation_view(request,slug,format):
    """Returns view to allow citation to be downloaded to citation management software."""
    p = get_object_or_404(Report,slug=slug)
    if format=="ris":
        template_file = 'cv/citations/report.ris'
        mime='application/x-research-info-systems'
    else:
        template_file = 'cv/citations/report.bib'
        mime='application/x-bibtex'
    return render(request, template_file, {'report':p},content_type=mime)

class TalkListView(generic.ListView):
    """
    Return list of articles.
    
    """
    
    model=Talk
    template_name = 'cv/lists/talk_list.html'
    context_object_name = 'talk_list'
    
class TalkDetailView(generic.DetailView):
    """
    Return view of a single talk.
    
    """
    
    model = Talk
    template_name = 'cv/details/talk_detail.html'
    context_object_name = 'talk'    

def talk_citation_view(request,slug,format):
    """Returns view to allow citation to be downloaded to citation management software."""
    p = get_object_or_404(Talk,slug=slug)
    if format=="ris":
        template_file = 'cv/citations/talk.ris'
        mime='application/x-research-info-systems'
    else:
        template_file = 'cv/citations/talk.bib'
        mime='application/x-bibtex'
    return render(request, template_file, {'talk':p},content_type=mime)

class GrantListView(generic.ListView):
    """
    Return list of grants.
    
    """
    
    model=Grant
    template_name = 'cv/lists/grant_list.html'
    context_object_name = 'grant_list'
    
class GrantDetailView(generic.DetailView):
    """
    Return view of a single grant.
    
    """
    
    model = Grant
    template_name = 'cv/details/grant_detail.html'
    context_object_name = 'grant'   


# Abstracted Model Views
class CVListView(generic.ListView):
    """Returns view of all instances for a particular object."""

    def dispatch(self, request, *args, **kwargs):
        """Set class parameters based on URL and dispatch."""
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv', self.model_name)
        self.context_object_name = (
            '%s' % ''.join(self.model._meta.verbose_name_plural))
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """
        Returns the name template to use to display a list of model instances.

        Currently returns ``cv/lists/<model_name>_list.html``.

        Might add a generic template for vitae models in the future.
        """
        return ['cv/lists/%s_list.html' % (self.model_name)]


class CVDetailView(generic.DetailView):

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv', self.model_name)
        self.context_object_name = (
            '%s' % ''.join(self.model._meta.verbose_name))
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return ['cv/details/%s_detail.html' % (self.model_name)]

# Forms
from django.views.generic.edit import CreateView, UpdateView, DeleteView, SingleObjectTemplateResponseMixin
from django.urls import reverse_lazy
from django.apps import apps
from .forms import authorship_formset_factory, edition_formset_factory

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
    'service': ['role', 'group', 'organization', 'type', 'start_date', 
                'end_date', 'description'],
    'student': ['first_name', 'last_name', 'middle_name', 'student_level',
                'role', 'thesis_title', 'is_current_student', 
                'graduation_date', 'first_position', 'current_position'],
    'article': ['title', 'status', 'display', 'submission_date', 'pub_date',
                'short_title', 'slug', 'abstract', 'journal', 'volume',
                'issue', 'start_page', 'end_page', 'url', 'series',
                'number', 'doi', 'pmcid', 'pmid', 'grants',
                'primary_discipline', 'other_disciplines', 'extra'],
    'book': ['title', 'short_title', 'slug', 'status', 'display',
             'submission_date', 'pub_date', 'abstract', 'publisher',
             'place', 'volume', 'series', 'series_number', 'num_pages',
             'isbn', 'url', 'grants','primary_discipline', 'other_disciplines', 
             'extra'],
    'otherwriting': ['title', 'short_title', 'slug', 'type', 'venue', 'date', 'pages', 'url', 'place', 
                     'volume', 'issue', 'abstract']
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
        self.formset = authorship_formset_factory(self.model_name)
        self.edition_formset = edition_formset_factory()
        if self.model_name=='book':
            self.edition_formset = edition_formset_factory()
        return context

    def get_template_names(self):
        """
        Return a list of template names to be used for the form to create
        a new object. Returns either:
        * ``cv/forms/<model_name>_add_form.html`` or
        * the ``template_name`` defined for the view
        """
        return ['cv/forms/%s_%s_form.html' % (self.model_name, self.method),
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
        if self.formset:
            if self.request.POST:
                context['authorship_formset'] = self.formset(self.request.POST)
            else:
                context['authorship_formset'] = self.formset()
        if self.edition_formset:
            if self.request.POST:
                context['edition_formset'] = self.edition_formset(self.request.POST)
            else:
                context['edition_formset'] = self.edition_formset()

        context['action_url'] = reverse_lazy(
            'cv:cv_add',
            kwargs={'model_name': self.model_name}
        )
        return context

    def form_valid(self, form):
        """Save authorship formset data if valid."""
        context = self.get_context_data()
        if self.formset:
            formset = context['authorship_formset']
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

    def get_context_data(self, **kwargs):
        context = super(CVUpdateView, self).get_context_data(**kwargs)
        if self.formset:
            if self.request.POST:
                context['authorship_formset'] = self.formset(
                    self.request.POST,
                    instance=self.object)
                context['authorship_formset'].full_clean()
            else:
                context['authorship_formset'] = self.formset(
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

class CVDeleteView(DeleteView):
    success_url = reverse_lazy('cv:cv_list')
    template_name = 'cv/forms/cv_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs['model_name']
        self.model = apps.get_model('cv',self.model_name)
        return super().dispatch(request, *args, **kwargs)
