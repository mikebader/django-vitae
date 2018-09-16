from django.apps import apps
from django.forms import inlineformset_factory

from cv.models import Book, BookEdition

# ArticleAuthorshipFormset = inlineformset_factory(
#                             Article,ArticleAuthorship,
#                             fields=['collaborator','print_middle','display_order','student_colleague']
#                             )
formset_fields = {
    'article': ['collaborator', 'print_middle', 'display_order',
                'student_colleague'],
    'book': ['collaborator', 'print_middle', 'display_order', 
             'student_colleague']
}


def authorship_formset_factory(model_name=None, **kwargs):
    """Return authorship formset for model if exists or None otherwise."""
    model = apps.get_model('cv', model_name)
    try:
        authorship_model = apps.get_model('cv', '%sauthorship' % model_name)
        return inlineformset_factory(
            model, authorship_model, fields=formset_fields[model_name], **kwargs)
    except LookupError:
        return None

def edition_formset_factory(**kwargs):
    """Manipulate the editions of a book."""
    return inlineformset_factory(Book, BookEdition,
        fields=['edition', 'pub_date', 'submission_date', 'publisher',
                'place', 'num_pages', 'isbn'], **kwargs)



class AuthorshipFormset:
    """Instance of authorship formset;
    Refactored to ``authorship_formset_factory`` function above"""
    def __init__(self, model_name,fields=None):
        self.model_name = model_name
        self.model = apps.get_model('cv', model_name)
        self.authorship_model = apps.get_model('cv', '%sauthorship' % model_name)
        self.formset = inlineformset_factory(
            self.model, self.authorship_model, fields=fields)

