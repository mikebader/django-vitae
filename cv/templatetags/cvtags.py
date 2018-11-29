from django.conf import settings
from django import template
from django.template.loader import get_template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

import cv.settings
from cv.models import Collaborator, GrantCollaboration, ChapterEditorship
from cv.utils import CSLCitation

register = template.Library()
key_contributor_list = cv.settings.CV_KEY_CONTRIBUTOR_LIST


def return_start_end_strings(collab):
    if (collab.email) in key_contributor_list:
        return "<span class='author-emphasis'>", "</span>"
    return "", ""


def construct_name(obj, first="given", highlight_key_authors=True):
    """Create string of authors name in conventional order
    (first, middle, last)."""
    print_middle = False
    # Following checks to see if the object passed is a Collaborator
    if type(obj) != Collaborator:
        collab = obj.collaborator
        print_middle = obj.print_middle
    else:
        collab = obj
    start_text, end_text = "", ""
    if highlight_key_authors:
        start_text, end_text = return_start_end_strings(collab)
    if first == "given":
        if print_middle:
            return '{}{} {} {}{}'.format(
                start_text, collab.first_name, collab.middle_initial,
                collab.last_name, end_text)
        return '{}{} {}{}}'.format(
            start_text, collab.first_name, collab.last_name, end_text)
    if print_middle:
        return '{}{}, {} {}{}'.format(
            start_text, collab.last_name, collab.first_name,
            end_text, collab.middle_initial)
    return '{}{}, {}{}' % (
        start_text, collab.last_name, collab.first_name, end_text)


@register.filter
def print_authors(value, first="given"):
    '''Print author list for publications and grants.'''
    if not value:
        return ''
    name_list = [construct_name(author) for author in value]
    if len(name_list) > 1:
        name_list[-1] = 'and {}'.format(name_list[-1])
    if len(name_list) >= 3:
        return mark_safe(', '.join(name_list))
    return mark_safe(' '.join(name_list))


@register.filter
def print_authors_bib_format(value):
    if not value:
        return ''
    name_list = [
        construct_name(author, first="family", highlight_key_authors=False)
        for author in value
    ]
    return mark_safe(' and '.join(name_list))


@register.filter(needs_autoescape=False)
def year_range(value, arg="–", autoescape=True):
    '''Return values of start date year and end date year'''
    if value.end_date:
        if value.start_date and value.start_date.year != value.end_date.year:
            return mark_safe('{}{}{}'.format(
                value.start_date.year, arg, value.end_date.year))
        return mark_safe(value.end_date.year)
    return mark_safe(value.start_date.year) + mark_safe(arg)
#   return mark_safe('%s%s') % (value.start_date.year,arg)


@register.filter
def monetize(value, sign="$"):
    '''Return value with currency sign and number with commas'''
    return "{}{}".format(sign, intcomma(int(value)))


@register.filter
def editors(value):
    if not value:
        return ''
    editors = value.editors.all()
    return print_authors(editors)


def make_param_values(name):
    params = ['last_name', 'first_name', 'middle_initial']
    if name:
        names = [i.strip() for i in name.split(",")]
        return {k: v for k, v in zip(params[0:len(names)], names)}
    return {}


@register.filter
def grant_role(value, name):
    param_vals = make_param_values(name)
    try:
        return value.grantcollaborator_set.get(
            collaborator_id=Collaborator.objects.get(**param_vals)).role
    except (Collaborator.DoesNotExist, GrantCollaboration.DoesNotExist) as e:
        return str(e)


@register.filter
def grant_pi_list(value, filter_name=None):
    param_vals = dict()
    if filter_name:
        param_vals = make_param_values(filter_name)
        value = value.exclude(**param_vals)
    return value.exclude(**param_vals)


@register.filter
def write_entry(instance):
    parts = CSLCitation(instance).entry_parts()
    year = parts[0].year if parts[0] else ''
    entry_str = format_html(
        (
            '<span class="cv-entry-date col-xs-2 col-sm-1">{}</span>\n'
            '<span class="cv-entry-text col-xs-9 col-sm-10">{}</span>\n'
        ), instance.slug, year, format_html(parts[1]))
    return entry_str


@register.inclusion_tag(
    'cv/_publication_entries.html', takes_context=True)
def publication_entries(context, publist, forthcoming='forth.'):
    """Applies template formatting to publication models."""
    model_name = publist[0]._meta.model_name
    publications = list()
    for pub in publist:
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


@register.simple_tag(takes_context=True)
def add_publication(context, model_name):
    """Create link to create new instance of model in template.

    Returns:
        if user is authenticated:
            Rendered context of link to add using cv/_publication_add.html
            template
        else: 
            Empty string
    """
    user = context['user']
    if user.is_authenticated:
        t = get_template('cv/_publication_add.html')
        context = {
            'model_name': model_name,
            'user': context['user']
        }
        return t.render(context)
    return ''

