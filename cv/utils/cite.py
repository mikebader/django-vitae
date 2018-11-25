from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc.source.json import CiteProcJSON
from citeproc_styles import get_style_filepath

from django.apps import apps
from django.conf import settings

from cv.settings import INREVISION_RANGE, CITE_CSL_STYLE, ENTRY_CSL_STYLE

import datetime
import os
from pathlib import Path


class CSLError(Exception):
    """Base exception for CSL functions."""
    pass


class CSLKeyError(CSLError):
    """Exception to define missing key for CSL type.CSL

    Attributes:
        type -- citation type (e.g., article, chapter)
        key -- dictionary key that cannot be left blank
    """
    def __init__(self, type, key):
        msg = 'Cannot cite \'{0}\' when \'{1}\' is undefined'.format(
            type, key)
        self.message = msg

    def __str__(self):
        return self.message


class CSLStyle:
    """Defines CSL style to be used in a citation."""

    def __init__(self, style=CITE_CSL_STYLE):
        """Create CSL style.

        Args:
            style: Name of a CSL style definition file (without suffix);
                defaults to ``CITE_CSL_STYLE`` from ``cv.settings``
        """
        self.style = style
        self.style_path = self.retrieve_csl_style()

    def retrieve_csl_style(self):
        """Returns file path to CSL style definition for ``style``.

        Returns:
            A file path to CSL stylesheet.

            This function searches for the CSL definition file in the ``csl``
            subdirectory of the ``BASE_DIR`` defined in the projects
            ``settings.py`` file and then in the ``csl`` subdirectory of the
            application directory (i.e., ``cv``).

            If a file with the style name cannot be found in one of those two
            directories, the function will use the ``get_style_filepath()``
            method from the :mod:`citeproc_styles` module.

        Raises:
            StyleNotFoundError: No matching CSL file exists in any of the
                searched paths.

        """

        file_locations = [
            os.path.abspath(os.path.join(settings.BASE_DIR, 'cv/csl')),
            os.path.abspath(apps.get_app_config('cv').path)
        ]
        for file_location in file_locations:
            style_path = Path(os.path.join(
                file_location, "csl", "{}.csl".format(self.style)))
            if style_path.is_file():
                return(style_path)
        return get_style_filepath(self.style)


class CSLCitation(object):
    """Citation object in CSL format for type of work product.

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
        self.fields = self.map_fields()

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
            given = given.rstrip('.').rstrip()
            family = collaborator.last_name
            collaborator_list.append({'given': given, 'family': family})
        return collaborator_list

    def _return_page_range(self):
        if self.instance.start_page:
            return '{}-{}'.format(self.instance.start_page,
                                  self.instance.end_page)
        return ''

    def map_fields(self):
        """Maps CSL attributes to fields by publication type.

        Returns:
           A dict mapping CSL attributes to the values retrieved from the
           database.
        """
        model_name = self.instance._meta.model_name
        fields = {
            'id': self.instance.slug,
            'title': self.instance.title,
            'author': self._return_collaborators(),
            'abstract': self.instance.abstract_html,
            'status': self.instance.get_status_display(),
            'title-short': self.instance.short_title,
        }
        if self.instance.url:
            fields['URL'] = self.instance.url
        if model_name == 'article':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                fields.update({
                    'type': 'article-journal',
                    'container-title': '{}'.format(
                        '' if not self.instance.journal
                        else self.instance.journal.title),
                    'DOI': self.instance.doi,
                    'issue': self.instance.issue,
                    'page': self._return_page_range(),
                    'PMCID': self.instance.pmcid,
                    'PMID': self.instance.pmid,
                    'volume': self.instance.volume,
                })
                fields.update(self._return_date_parts())
            else:
                fields['type'] = 'article'
        elif model_name == 'book':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                fields.update({
                    'type': 'book',
                    'collection-title': self.instance.series,
                    'collection-number': self.instance.series_number,
                    'volume': self.instance.volume,
                    'publisher': self.instance.publisher,
                    'publisher-place': self.instance.place,
                })
                if self.edition:
                    fields['edition'] = self.edition.edition
                    fields.update(self.edition._return_date_parts())
                    fields['ISBN'] = self.edition.isbn
                else:
                    fields.update(self._return_date_parts())
                    fields['ISBN'] = self.instance.isbn
            else:
                fields['type'] = 'manuscript'
        elif model_name == 'chapter':
            if len(self.instance.editorship.all()) < 1:
                raise CSLKeyError('chapter', 'editorship')
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                fields.update({
                    'container-title': self.instance.book_title,
                    'type': 'chapter',
                    'ISBN': self.instance.isbn,
                    'page': self._return_page_range(),
                    'publisher': self.instance.publisher,
                    'publisher-place': self.instance.place,
                    'collection-title': self.instance.series,
                    'collection-number': self.instance.series_number,
                    'volume': self.instance.volume,
                    'editor': self._return_collaborators(
                        collaboration_type='editorship')
                })
                fields.update(self._return_date_parts())
            else:
                fields['type'] = 'manuscript'
        elif model_name == 'report':
            if ((self.instance.pub_date or self.instance.submission_date) and
               self.instance.status >= INREVISION_RANGE.min):
                fields.update({
                    'type': 'report',
                    'publisher': self.instance.institution,
                    'publisher-place': self.instance.place,
                    'number': self.instance.report_number,
                    'genre': self.instance.report_type,
                    'collection-title': self.instance.series_title
                })
                fields.update(self._return_date_parts())
            else:
                fields['type'] = 'manuscript'
        for k, v in fields.items():
            fields[k] = v if v is not None else ''
        return fields

    def cite(self, fmtr, style=CITE_CSL_STYLE, doi=True):
        if doi is False:
            self.fields['DOI'] = ''
        style_path = CSLStyle(style).style_path
        bib_style = CitationStylesStyle(str(style_path), validate=False)
        bibliography = CitationStylesBibliography(
            bib_style, CiteProcJSON([self.fields]), fmtr)
        citation = Citation([CitationItem(self.instance.slug)])
        bibliography.register(citation)
        cite = str(bibliography.bibliography()[0]).replace('..', '.')
        return cite

    def cite_html(self, style=CITE_CSL_STYLE, **kwargs):
        """Returns an HTML-formatted citation of model instance."""
        return self.cite(formatter.html, style, **kwargs)

    def cite_plain(self, style=CITE_CSL_STYLE, **kwargs):
        """Returns plain-text citation of model instance."""
        return self.cite(formatter.plain, style, **kwargs)

    def entry_parts(self, fmt='html', style=ENTRY_CSL_STYLE, **kwargs):
        if 'issued' in self.fields:
            date = self.fields.pop('issued')
            date = datetime.datetime(*list(map(int, date['date-parts'][0])))
        else:
            date = None
        if fmt == 'html':
            return (date, self.cite_html(style, **kwargs))
        return (date, self.cite_plain(style, **kwargs))
