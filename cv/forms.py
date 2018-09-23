from django.apps import apps
from django.forms import inlineformset_factory

from cv.models import Book, BookEdition, \
                      Chapter, ChapterEditorship, \
                      Grant, GrantCollaboration


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
        fields=['collaborator', 'role', 'is_pi'],
        **kwargs
    )
