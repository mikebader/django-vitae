"""Settings for Django-CV"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from collections import namedtuple
import re

CV_PUBLICATION_STATUS_CHOICES = (
    (0,'INPREP',_('In preparation')),
    (1,'WORKING',_('Working paper')),
    (20,'SUBMITTED',_('Submitted')),
    (30,'REVISE',_('Revise')),
    (35,'RESUBMITTED',_('Resubmitted')),
    (40,'CONDACCEPT', _('Conditionally accepted')),
    (50,'FORTHCOMING',_('Forthcoming')),
    (55,'INPRESS', _('In press')),
    (60,'PUBLISHED',_('Published')),
    (99,'RESTING',_('Resting'))
    )

CV_STUDENT_LEVELS_CHOICES =(
    (0,'UNDERGRAD',_('Undergraduate student')),
    (10,'MASTERS',_('Masters student')),
    (20,'DOCTORAL',_('Doctoral student'))
    )

CV_SERVICE_TYPES_CHOICES = (
    (10,'DEPARTMENT',_('Department')),
    (20,'SCHOOL', _('School or College')),
    (30,'UNIVERSITY',_('University-wide')),
    (40,'DISCIPLINE',_('Discipline')),
    (50,'COMMUNITY',_('Community')),
    (90,'OTHER',_('Other'))
    )

CV_FILE_TYPES_CHOICES = (
    (10, 'MANUSCRIPT_FILE', _('Manuscript')),
    (20, 'PREPRINT_FILE', _('Preprint')),
    (30, 'DRAFT_FILE', _('Draft')),
    (40, 'SLIDE_FILE', _('Slides')),
    (50, 'CODE_FILE', _('Code')),
    (60, 'TABLE_FILE', _('Table')),
    (70, 'IMAGE_FILE', _('Image')),
    (80, 'SUPPLEMENT_FILE', _('Supplement')),
    (100, 'OTHER_FILE', _('Other'))
)

CV_TERMS_CHOICES = (
    (10, 'WINTER', _('Winter')),
    (20, 'SPRING', _('Spring')),
    (30, 'SUMMER', _('Summer')),
    (40, 'FALL', _('Fall'))
)

def make_choice_list(val,default,suffix=""):
    """Return tuple of choices for inclusion in model and dictionary with keys
    representing each choice and values equal to the integer value"""
    suffix = '_%s' % suffix if suffix else ''       
    choice_list = getattr(settings,val,default)
    choice_dict = dict()
    for choice in choice_list:
        if not (len(choice)==3 and 
                   isinstance(choice[0], int) and 
                   re.match("^[^\d\s]\w+$",choice[1]) and
                   isinstance(str(choice[2]), str)):
            raise ValueError(_("Custom choice lists must contain tuples with three values of formats ``(int,str,str)``"))
        choice_label = '%s%s' % (choice[1],suffix)
        choice_dict[choice_label]=choice[0]
    return ([(tup[0],tup[2]) for tup in choice_list],choice_dict)

(PUBLICATION_STATUS_CHOICES, PUBLICATION_STATUS) = make_choice_list(
                                            'CV_PUBLICATION_STATUS_CHOICES',
                                            CV_PUBLICATION_STATUS_CHOICES,
                                            suffix="STATUS")

(STUDENT_LEVELS_CHOICES,STUDENT_LEVELS) = make_choice_list(
                                            'CV_STUDENT_LEVELS_CHOICES',
                                            CV_STUDENT_LEVELS_CHOICES,
                                            suffix="STUDENT")

(SERVICE_TYPES_CHOICES,SERVICE_TYPES) = make_choice_list(
                                            'CV_SERVICE_TYPES_CHOICES',
                                            CV_SERVICE_TYPES_CHOICES,
                                            suffix="SERVICE")

(FILE_TYPES_CHOICES, FILE_TYPES) = make_choice_list(
                                            'CV_FILE_TYPES_CHOICES',
                                            CV_FILE_TYPES_CHOICES,
                                            suffix='FILE')

(TERMS_CHOICES, TERMS) = make_choice_list(
                                            'CV_TERMS_CHOICES',
                                            CV_TERMS_CHOICES,
                                            suffix='TERM')

CV_PERSONAL_INFO = getattr(settings,'CV_PERSONAL_INFO','')

CV_KEY_CONTRIBUTOR_LIST = getattr(settings,'CV_KEY_CONTRIBUTOR_LIST','')

MinMax = namedtuple('MinMax','min max')
INPREP_RANGE = MinMax(0, 10)
INREVISION_RANGE = MinMax(20, 50)
PUBLISHED_RANGE = MinMax(50, 90)

CSL_STYLE = getattr(settings,'CV_CSL_STYLE','harvard1')
