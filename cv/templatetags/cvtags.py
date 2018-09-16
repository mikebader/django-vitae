from django.conf import settings
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

import cv.settings
from cv.models import Collaborator, GrantCollaboration, ChapterEditorship

register = template.Library()
key_contributor_list = cv.settings.CV_KEY_CONTRIBUTOR_LIST

## TODO:
##    * Add function for last, first; provide option on tag for name ordering
##    * Incorporate citeproc into tags to allow citeproc/csl citation processing

def return_start_end_strings(collab):
	if (collab.email) in key_contributor_list:
		return "<span class='author-emphasis'>","</span>"
	return "",""
		
def construct_name(obj,first="given",highlight_key_authors=True):
	'''Create string of authors name in conventional order (first, middle, last).'''
	print_middle = False
	## Following checks to see if the object passed is a Collaborator
	if type(obj)!=Collaborator:
		collab = obj.collaborator
		print_middle = obj.print_middle
	else:
		collab = obj
	start_text, end_text = "",""
	if highlight_key_authors:
		start_text, end_text = return_start_end_strings(collab)
	if first=="given":
		if print_middle:
			return '%s%s %s %s%s' % (start_text,collab.first_name, collab.middle_initial, collab.last_name,end_text)
		return '%s%s %s%s' % (start_text,collab.first_name, collab.last_name,end_text)
	if print_middle:
		return '%s%s, %s %s%s' % (start_text,collab.last_name, collab.first_name,end_text, collab.middle_initial)
	return '%s%s, %s%s' % (start_text,collab.last_name, collab.first_name,end_text)
		

@register.filter
def print_authors(value,first="given"):
	'''Print author list for publications and grants.'''
	if not value:
		return ''
	name_list = [construct_name(author) for author in value]
	if len(name_list)>1:
		name_list[-1] = 'and %s' % name_list[-1]
	if len(name_list)>=3:
		return mark_safe(', '.join(name_list))
	return mark_safe(' '.join(name_list))

@register.filter
def print_authors_bib_format(value):
	if not value:
		return ''
	name_list = [construct_name(author,first="family",highlight_key_authors=False) for author in value]
	return mark_safe(' and '.join(name_list))

@register.filter(needs_autoescape=False)
def year_range(value,arg="&#8211;",autoescape=True):
	'''Return values of start date year and end date year'''
	if value.end_date:
		if value.start_date and value.start_date.year!=value.end_date.year:
			return mark_safe('%s&#8211;%s' % (value.start_date.year,value.end_date.year))
		return mark_safe(value.end_date.year)
	return mark_safe(value.start_date.year)+mark_safe(arg)
#	return mark_safe('%s%s') % (value.start_date.year,arg)
	
@register.filter
def monetize(value,sign="$"):
	'''Return value with currency sign and number with commas'''
	return "%s%s" % (sign, intcomma(int(value)))

@register.filter
def editors(value):
	if not value:
		return ''
	editors = value.chaptereditorship_set.all()
	return print_authors(editors)

def make_param_values(name):
	params = ['last_name','first_name','middle_initial']
	if name: 
		names = [i.strip() for i in name.split(",")]
		return {k:v for k,v in zip(params[0:len(names)],names)}
	return {}
	
@register.filter
def grant_role(value,name):
	param_vals = make_param_values(name)
	try:
 		return value.grantcollaborator_set.get(
 						collaborator_id=Collaborator.objects.get(**param_vals)).role
	except (Collaborator.DoesNotExist,GrantCollaborator.DoesNotExist) as e:
		return str(e)

@register.filter
def grant_pi_list(value,filter_name=None):
	param_vals = dict()
	if filter_name: 
		param_vals = make_param_values(filter_name)
		value = value.exclude(**param_vals)
	return value.exclude(**param_vals)
	
	