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
