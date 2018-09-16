"""Tests for Django-CV Report model"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.settings import PUBLICATION_STATUS, STUDENT_LEVELS
from cv.models import Report, ReportAuthorship, BookEdition

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase


@attr('report')
class ReportTestCase(VitaePublicationTestCase, AuthorshipTestCase):

    @classmethod
    def setUp(cls):
        super(ReportTestCase, cls).setUp()

        s = {
            'title': 'States\' laws on race and color',
            'short_title': 'States\' laws',
            'slug': 'states-laws',
            'pub_date': '1950-01-01',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS'],
        }

        m = {
            'title': ('A Proposal to Reexamine the Applicability of the '
                      'Fourteenth Amendment to State Laws and Practices '
                      'Which Discriminate on the Basis of Sex Per Se'),
            'short_title': 'Proposal to Reexamine Fourteenth Amendment',
            'slug': 'proposal-to-rexamine',
            'pub_date': '1961-01-01',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }

        h = {
            'title': 'Human Rights U.S.A.:  1948-1966',
            'short_title': 'Human Rights U.S.A.',
            'slug': 'human-rights-usa',
            'pub_date': '1967-01-01',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }

        cls.extra_report_params = {
            'title': 'this is a very long title',
            'short_title': 'short title',
            'slug': 'short-title',
            'status': PUBLICATION_STATUS['INPREP_STATUS']
        }

        for report_params in [s, m, h]:
            r = Report.objects.create(**report_params)
            authorship = ReportAuthorship(
                collaborator=cls.murray, report=r, display_order=1)
            authorship.save()

    def add_student_author_to_report(self, report):
        """Add student collaborator as author to report."""
        ReportAuthorship(
            report=report, collaborator=self.dill, display_order=2,
            student_colleague=STUDENT_LEVELS['DOCTORAL_STUDENT']).save()
        return report

    def test_report_string(self):
        r = Report.objects.get(slug='states-laws')
        self.assertEqual('States\' laws', str(r))

    def test_report_required_fields(self):
        req_fields = ['title', 'short_title', 'slug', 'status']
        for field in req_fields:
            report = self.extra_report_params.copy()
            report.pop(field)
            try:
                Report.objects.create(**report)
            except ValidationError as e:
                if field == 'status':
                    self.assertIn('This field cannot be null',
                                  str(e.error_dict[field][0]))
                else:
                    self.assertIn('This field cannot be blank',
                                  str(e.error_dict[field][0]))
            else:
                report.save()
                raise ValidationError(_('Report should not be saved without '
                                        'required field %s') % field)
                report.delete()

    def test_report_slug_uniqueness(self):
        """Test that model cannot be saved with duplicate slug."""
        self.extra_report_params['slug'] = 'states-laws'
        try:
            Report.objects.create(**self.extra_report_params)
            raise AssertionError('Report model does not save unique slugs')
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Report with this Slug already exists',
                          str(e.error_dict['slug'][0]))

    def test_report_single_author(self):
        """Test that single authorship works correctly."""
        r = Report.objects.create(**self.extra_report_params)
        auth = ReportAuthorship(
            report=r, collaborator=self.murray, display_order=1)
        auth.save()
        self.assertAuthorshipLength(r, 1)

    def test_report_multiple_author(self):
        """Test that authorship model returns currect number of authors."""
        r = Report.objects.get(slug='proposal-to-rexamine')
        r = self.add_student_author_to_report(r)
        self.assertAuthorshipLength(r, 2)

    def test_report_authorship_order(self):
        """Test that authors display in assigned order."""
        r = Report.objects.get(slug='proposal-to-rexamine')
        r = self.add_student_author_to_report(r)
        authors = ['Murray, Pauli', 'Dill, Augustus G.']
        self.assertAuthorshipDisplayOrder(r, authors)

    def test_report_authorship_order_unique(self):
        """Test that display_order may not be repeated for a chapter."""
        report = Report.objects.get(slug='proposal-to-rexamine')
        auth = ReportAuthorship(
            collaborator=self.dill, report=report, display_order=1)
        err_msg = ('Report authorship with this Report and '
                   'Display order already exists.')
        with self.assertRaisesMessage(ValidationError, err_msg):
            auth.save()

    def test_chapter_authorship_student_collaboration(self):
        """Test student colleague status for report authorship."""
        r = Report.objects.get(slug='states-laws')
        r = self.add_student_author_to_report(r)
        self.assertAuthorshipStudentStatus(
            r, ['dill@example.com'], ['pauli.murray@example.com'])

    # test methods
    # save
    def test_report_abstract_markdown(self):
        """Test that markdown input on abstract gets converted to HTML."""
        r = Report.objects.get(slug='states-laws')
        r.abstract = ('_Thurgood Marshall_ called this **the bible** of '
                      'civil rights law.')
        r.save()
        self.assertEqual(r.abstract_html,
                         '<p><em>Thurgood Marshall</em> called this '
                         '<strong>the bible</strong> of civil rights law.'
                         '</p>')

    def test_report_status_fields(self):
        """Test whether status flag fields are correct on create and update."""
        for value in Report._meta.get_field('status').choices:
            fields = self.extra_report_params.copy()
            fields['status'] = value[0]
            r = Report.objects.create(**fields)
            self.assess_status_values(r, value)
            r.delete()
        fields = self.extra_report_params.copy()
        r = Report.objects.create(**fields)
        for value in Report._meta.get_field('status').choices:
            r.status = value[0]
            r.save()
            self.assess_status_values(r, value)

    # get_absolute_url
    def test_report_get_absolute_url(self):
        """Test that instance returns correct url."""
        r = Report.objects.get(slug='states-laws')
        self.assertEqual("/reports/states-laws/",
                         r.get_absolute_url())

    # custom methods
    def test_report_get_next_previous_published_status(self):
        """Test that get_next_by_status() returns published report."""
        r = Report.objects.get(slug='proposal-to-rexamine')
        self.assertNextByStatus(r, 'human-rights-usa')
        self.assertPreviousByStatus(r, 'states-laws')

    def test_report_get_next_previous_inrevision(self):
        for r in Report.objects.all():
            r.status = PUBLICATION_STATUS['SUBMITTED_STATUS']
            r.submission_date = r.pub_date
            r.save()
        r = Report.objects.get(slug='proposal-to-rexamine')
        self.assertNextByStatus(r, 'human-rights-usa')
        self.assertPreviousByStatus(r, 'states-laws')

    def test_report_get_next_previous_inprep(self):
        """Test that in-preparation files cannot return value for
        get_next_previous_by_status()."""
        for r in Report.objects.all():
            r.status = PUBLICATION_STATUS['INPREP_STATUS']
            r.submission_date = r.pub_date
            r.save()
        r = Report.objects.get(slug='proposal-to-rexamine')
        self.assertNoNextPreviousByStatus(r)
