from django import template
from django.template.loader import get_template

from django.apps import apps
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from cv.utils import CSLCitation

register = template.Library()

## List Inclusion Tags
@register.inclusion_tag(
    'cv/_entries_publication.html', takes_context=True)
def publication_entries(context, pubqs, forthcoming='forth.'):
    """Applies template formatting to publication models.

    :param pubqs: QuerySet containing publication instances
    :type pubqs: :class:`~django.db.models.query.QuerySet`
    :param forthcoming: String instructing how to reference forthcoming
                        publications
    :type forthcoming: str, optional

    Takes a :class:`QuerySet` of publications and returns formatted list of
    publications based on Constructs publication based on template stored in
    ``cv/_entries_publication.html``.

    """
    model_name = pubqs[0]._meta.model_name
    publications = list()
    for pub in pubqs:
        parts = CSLCitation(pub).entry_parts()
        year = parts[0].year if parts[0] else ''
        if pub.get_status_display() == "Forthcoming":
            year = forthcoming
        pubdict = dict(
            publication=pub, date=year,
            entry=format_html(parts[1]))
        publications.append(pubdict)
    return{
        'model_name': model_name,
        'publications': publications,
        'user': context['user']}


@register.inclusion_tag('cv/_list_publication.html', takes_context=True)
def publication_list(context, model_name, qsdict):
    """Formatted list of publications by publication status.

    :param model_name: Section name
    :type model_name: str
    :param qsdict: Dictionary containing keys ``published``, ``inprep``, and
                   ``revise`` keys with QuerySets as values
    :type qsdict: dict

    Takes a dictionary of publication types (published, in preparation,
    and under revision) and returns formatted the publication list based on
    the template stored in ``cv/_list_publication.html``.

    """
    return dict([
        ('model_name', model_name),
        ('object_list', qsdict),
        ('user', context['user'])
    ])


@register.inclusion_tag('cv/_list.html', takes_context=True)
def section_list(context, model_name, qs, section_name=None):
    section_template = 'cv/sections/{}.html'.format(model_name)
    plural_name = apps.get_model('cv', model_name)._meta.verbose_name_plural
    section_name = section_name if section_name else plural_name
    return dict([
        ('model_name', model_name,),
        ('section_name', section_name),
        ('object_list', qs),
        ('section_template', section_template),
        ('user', context['user'])
    ])


# Item tags
@register.simple_tag(takes_context=True)
def add_item(context, model_name):
    """Formatted link to form to add new instance of model.

    :param model_name: Name of model
    :type model: str

    Takes model name and returns formatted link to add new instance of model
    based on template stored in ``cv/_item_add.html``.
    """
    user = context['user']
    if user.is_authenticated:
        url = reverse('cv:cv_add', args=(model_name,))
        t = get_template('cv/_item_add.html')
        verbose_name = apps.get_model('cv', model_name)._meta.verbose_name
        context = dict([
            ('model_name', model_name),
            ('verbose_name', verbose_name),
            ('url', url),
            ('user', user)
        ])
        return t.render(context)
    return ''


@register.simple_tag(takes_context=True)
def edit_item(context, inst, text_before='', text_after=''):
    user = context['user']
    if user.is_authenticated:
        model_name = inst._meta.verbose_name
        verbose_name = model_name
        url = reverse('cv:cv_edit',
                      kwargs={'model_name': model_name, 'pk': inst.pk})
        t = get_template('cv/_item_edit.html')
        context = dict([
            ('text_before', text_before),
            ('text_after', text_after),
            ('model_name', model_name),
            ('verbose_name', verbose_name),
            ('url', url),
            ('user', user)
        ])
        return t.render(context)
    return ''


@register.simple_tag()
def cite_item(obj):
    """Html-formatted citation of object.

    :param obj: django-vitae object
    """
    return mark_safe(CSLCitation(obj).cite_html())


@register.simple_tag()
def cite_download(obj, fmt):
    """Create formatted link to citation.

    :param obj: A django-vitae object that contains a slug and citation
                templates
    :param fmt: String representing format, may be either 'ris' or 'bib'
    :type fmt: str

    Takes an object and format and returns a link to the citation formatted
    using the template ``cv/_cite_download.html``.
    """
    cite_url = reverse('cv:citation', kwargs={
        'model_name': type(obj).__name__.lower(),
        'slug': obj.slug,
        'format': fmt
    })
    t = get_template('cv/_cite_download.html')
    return t.render(dict([
        ('format', fmt,),
        ('cite_url', cite_url),
        ('object', obj)
    ]))


# Formatting tags
@register.simple_tag()
def print_collaborators(collaborators, sep=', ', two_sep=' and ',
                        last_sep=', and ', et_al_after=None, **kwargs):
    """Creates a formatted string of a queryset of collaborators."""
    num = et_al_after if et_al_after else len(collaborators)
    collaborators = [construct_name(a, **kwargs) for a in collaborators[0:num]]
    # print(authors)
    if len(collaborators) == 1:
        return collaborators[0]
    elif len(collaborators) == 0:   # Publication models need to check for
                                    # at least one author!!!
        return []
    final_sep = last_sep if len(collaborators) > 2 else two_sep
    return '{}{}{}'.format(
        sep.join(collaborators[:-1]), final_sep, collaborators[-1])


# Filters
@register.filter(needs_autoescape=False)
def year_range(value, sep="–"):
    """Return values of start date year and end date year.

    :param sep: String to display between start and end dates
    :type sep: string, optional, default = "-"

    """
    if value.end_date:
        if value.start_date and value.start_date.year != value.end_date.year:
            return mark_safe('{}{}{}'.format(
                value.start_date.year, sep, value.end_date.year))
        return mark_safe(value.end_date.year)
    return mark_safe(value.start_date.year) + mark_safe(sep)
#   return mark_safe('%s%s') % (value.start_date.year,arg)

@register.filter
def monetize(value, sign="$"):
    '''Return value with currency sign and number with commas'''
    return "{}{}".format(sign, intcomma(int(value)))
