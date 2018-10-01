from django.apps import apps
from django.forms import inlineformset_factory

from cv.models import Book, BookEdition, \
                      Chapter, ChapterEditorship, \
                      Grant, GrantCollaboration, \
                      Talk, Presentation, \
                      Course, CourseOffering


def get_authorship_fields():
    """Return list of fields for student collaborations."""
    return ('collaborator', 'print_middle', 'display_order',
            'student_colleague')


def authorship_formset_factory(model_name=None, **kwargs):
    """Return authorship formset for model if exists or None otherwise."""
    model = apps.get_model('cv', model_name)
    try:
        authorship_model = apps.get_model('cv', '%sauthorship' % model_name)
        return inlineformset_factory(
            model, authorship_model, fields=get_authorship_fields(), **kwargs)
    except LookupError:
        return None


def edition_formset_factory(**kwargs):
    """Manipulate the editions of a book."""
    return inlineformset_factory(
        Book, BookEdition,
        fields=['edition', 'pub_date', 'submission_date', 'publisher',
                'place', 'num_pages', 'isbn'], **kwargs
    )


def editorship_formset_factory(**kwargs):
    """Create formsets for editorships."""
    return inlineformset_factory(
        Chapter, ChapterEditorship,
        fields=get_authorship_fields()[0:3],
        **kwargs
    )


def grant_collaboration_formset_factory(**kwargs):
    """Create set of forms representing grang collaborations."""
    return inlineformset_factory(
        Grant, GrantCollaboration,
        fields=['collaborator', 'role', 'is_pi', 'display_order'],
        **kwargs
    )

def presentation_formset_factory(**kwargs):
    return inlineformset_factory(
        Talk, Presentation,
        fields=['presentation_date', 'event', 'event_acronym', 'city',
                'state', 'country', 'type'],
        **kwargs
    )


def offering_formset_factory(**kwargs):
    """Create set of forms for course offerings of a course."""
    return inlineformset_factory(
        Course, CourseOffering, 
        fields=['term', 'start_date', 'end_date', 'institution',
                'course_number'])
