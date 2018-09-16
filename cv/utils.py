from django.utils.translation import ugettext_lazy as _

import re


def check_isbn(isbn_raw):
    """
    Returns ISBN for well-formated ISBN candidates and throws
    ``ValueError`` otherwise.

    The function checks that the formatting of the ISBN to follows standards
    and that the final checksum digit is correct.
    """
    isbn = re.findall('[\dX]', isbn_raw.upper())
    isbn = "".join(isbn)
    m = re.fullmatch(r'\d{9}[0-9xX]|\d{13}', isbn)
    print(isbn)
    if m:
        isbn = m.group()
        if len(isbn) == 13:
            info = isbn[0:12]
            mult = [i for item in range(6) for i in [1, 3]]
            summed = sum([int(n) * v for n, v in zip(info, mult)])
            check_digit = 10 - (summed % 10)
            check_digit = str(check_digit) if check_digit != 10 else 0
            if check_digit == isbn[-1]:
                return isbn
        else:
            info = isbn[0:9]
            summed = sum([int(n) * v for n, v in zip(info, range(10, 0, -1))])
            check_digit = 11 - summed % 11
            check_digit = str(check_digit) if check_digit != 10 else "X"
            if check_digit == isbn[-1]:
                return isbn
        raise ValueError(_("Inproper checksum digit for ISBN, check "
                           "that you entered the ISBN correctly"))
    raise ValueError(_("Improperly formatted ISBN"))


from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc import types
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath

from django.apps import apps
from django.conf import settings 
from django.core import serializers

from cv.settings import INREVISION_RANGE, CSL_STYLE

import os
from pathlib import Path

# class CVCitationStylesStyle(CitationStylesStyle):


class CSLCitation(object):
    """Stores citation for publication in CSL format for type of work product.

    The field mappings from Django-CV objects to CSL are based on
    fieldmaps published at
    `<https://github.com/dsifford/csl-fieldmaps>`_

    https://aurimasv.github.io/z2csl/typeMap.xml#cslVar-issued

    An instance of this class enclosed in a list can be used with
    CiteProcJSON from the :mod:`citeproc` module to return
    citations. The CSL format used is defined in ``cv.settings.CSL`` custom
    setting. 

    Args:
        instance: an instance of a Django-CV work product

    Attributes:
        fields: a dictionary of CSL-recognized fields with values
                for instance

    """

    def __init__(self, instance, **kwargs):
        self.instance = instance
        self.edition = ''
        if 'edition' in kwargs.keys():
            self.edition = self.instance.editions.get(
                edition=kwargs['edition']
            )
        self.set_fields()
        print(os.path.abspath(os.path.join(
                os.path.dirname(__file__), os.pardir, 'csl')))

    def set_fields(self):
        model_name = self.instance._meta.model_name
        self.fields = {
            'id': self.instance.slug,
            'title': self.instance.title,
            'author': self._return_collaborators(),
            'abstract': self.instance.abstract_html,
            'status': self.instance.get_status_display(),
            'title-short': self.instance.short_title,
            'URL': self.instance.url
        }
        if model_name == 'article':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                self.fields.update({
                    'type': 'article-journal',
                    'container-title': '{}'.format(
                        '' if not self.instance.journal
                        else self.instance.journal.title),
                    'doi': self.instance.doi,
                    'issue': self.instance.issue,
                    'page': '{}-{}'.format(
                        self.instance.start_page,
                        self.instance.end_page),
                    'PMCID': self.instance.pmcid,
                    'PMID': self.instance.pmid,
                    'volume': self.instance.volume,
                })
                self.fields.update(self._return_date_parts())
            else:
                self.fields['type'] = 'article'
        elif model_name == 'book':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                self.fields.update({
                    'type': 'book',
                    'collection-title': self.instance.series,
                    'collection-number': self.instance.series_number,
                    'volume':
                        self.instance.volume if self.instance.volume else '',
                    'publisher': self.instance.publisher,
                    'publisher-place': self.instance.place,
                })
                if self.edition:
                    self.fields['edition'] = self.edition.edition
                    self.fields.update(self.edition._return_date_parts())
                    self.fields['ISBN'] = self.edition.isbn
                else:
                    self.fields.update(self._return_date_parts())
                    self.fields['ISBN'] = self.instance.isbn
            else:
                self.fields['type'] = 'manuscript'
        elif model_name == 'chapter':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                self.fields.update({
                    'type': 'chapter',
                    'ISBN': self.instance.isbn,
                    'page': '{}-{}'.format(
                        self.instance.start_page,
                        self.instance.end_page),
                    'publisher': self.instance.publisher,
                    'publisher-place': self.instance.place,
                    'collection-title': self.instance.series,
                    'collection-number': self.instance.series_number,
                    'volume':
                        self.instance.volume if self.instance.volume else '',
                    'editor': self._return_collaborators(
                        collaboration_type='editorship')
                })
                self.fields.update(self._return_date_parts())
            else:
                set.fields['type'] = 'manuscript'
        elif model_name == 'report':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                self.fields.update({
                    'type': 'report',
                    'publisher': self.instance.institution,
                    'publisher-place': self.instance.place,
                    'number': self.instance.report_number,
                    'genre': self.instance.report_type,
                    'collection-title': self.instance.series_title
                })
            else:
                self.fields['type'] = 'manuscript'

    def _return_date_parts(self, use_sub_date=False):
        if self.instance.pub_date:
            return {'issued': {'date-parts':
                    [str(self.instance.pub_date).split('-')]}}
        if self.instance.submission_date and use_sub_date:
            return {'submitted': {'date-parts':
                    [str(self.instance.submission_date).split('-')]}}
        return {'issued': {'date-parts': [['', '', '']]}}

    def _return_collaborators(self, collaboration_type='authorship'):
        collaboration_set = getattr(self.instance, collaboration_type)
        collaborator_list = []
        for collaboration in collaboration_set.all():
            collaborator = collaboration.collaborator
            given = '{} {}'.format(
                collaborator.first_name, collaborator.middle_initial)
            family = collaborator.last_name
            collaborator_list.append({'given': given, 'family': family})
        return collaborator_list

    def cite(self):
        style_path = get_style_filepath(CSL_STYLE)
        print(style_path)
        bib_style = CitationStylesStyle(style_path, validate=False)
        bibliography = CitationStylesBibliography(
            bib_style, CiteProcJSON([self.fields]), formatter.html)
        citation = Citation([CitationItem(self.instance.slug)])
        bibliography.register(citation)
        return str(bibliography.bibliography()[0])


def retrieve_csl_style(style=CSL_STYLE):
    """Returns file path to CSL style definition for ``style``.

    This function searches for the CSL definition file in the ``csl``
    subdirectory of the ``BASE_DIR`` defined in the projects ``settings.py``
    file and then in the ``csl`` subdirectory of the application directory
    (i.e., ``cv``).

    If a file with the style name cannot be found in one of those two
    directories, the function will use the ``get_style_filepath()``
    method from the :mod:`citeproc_styles` module. The method will return
    a ``StyleNotFoundError`` if no match exists in the
    :mod:`citeproc_styles` style repository.

    """

    file_locations = [
        os.path.abspath(settings.BASE_DIR),
        os.path.abspath(apps.get_app_config('cv').path)
    ]
    for file_location in file_locations:
        style_path = Path(os.path.join(
            file_location, "csl", "{}.csl".format(style)))
        if style_path.is_file():
            return(style_path)
    return get_style_filepath(style)
