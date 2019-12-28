from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr
from unittest import TestCase

from cv.models import (Journal, Collaborator,
                       Article, ArticleAuthorship,
                       Book, BookAuthorship,
                       Chapter, ChapterAuthorship, ChapterEditorship,
                       Report, ReportAuthorship)
from cv.settings import PUBLICATION_STATUS
from cv.utils import check_isbn, CSLKeyError, CSLCitation, CSLStyle
# from cv.utils.cite import retrieve_csl_style

import os
from pathlib import Path

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase


@attr('isbn')
class IsbnTestCase(TestCase):
    def test_check_isbn_function_well_formed(self):
        """Test that well-formed ISBNs pass check_isbn()."""
        real_isbn_13s = ['9780553418811', '9780553418811', '9780143127536', 
                         '9780520271425', ]
        real_isbn_10s = ['0553418831', '0143127535', '0520271424',
                         '014200068X', '014200068x']
        for isbn in real_isbn_13s:
            isbn = str(isbn).upper()  # check_isbn always returns uppercase 'X'
            self.assertEqual(isbn, check_isbn(isbn))
        for isbn in real_isbn_10s:
            self.assertEqual(isbn, check_isbn(isbn))

    def test_check_isbn_bad_checksum(self):
        """
        Test that a check_isbn throws error for bad checksum digit
        or transposed digit.
        """
        bad_checksum = '978-0-55-341881-3'
        with self.assertRaises(ValueError) as e:
            check_isbn(bad_checksum)
            self.assertIn(_("Inproper checksum digit for ISBN"),
                          str(e))
        transposed_digits = '9780554318811'
        with self.assertRaises(ValueError) as e:
            check_isbn(transposed_digits)
            self.assertIn(_("Inproper checksum digit for ISBN"),
                          str(e))

    def test_check_isbn_wrong_length(self):
        """Test that check_isbn() throws error for ISBN of wrong length."""
        bad_isbn = '978055341881'
        with self.assertRaises(ValueError) as e:
            check_isbn(bad_isbn)
            self.assertIn(_("Improperly formatted ISBN"),
                          str(e))


@attr('utils')
class UtilsTestCase(VitaePublicationTestCase, AuthorshipTestCase):
    """Test class to check utility functions in Django-CV."""

    @classmethod
    def setUp(cls):
        super(UtilsTestCase, cls).setUp()

        # Create article object to test citation
        j = Journal.objects.create(title='Scientific American')
        a = {
            'title': 'On the Generalized Theory of Gravitation',
            'short_title': 'Generalized Theory of Gravitation',
            'slug': 'gen-theory-gravitation',
            'pub_date': '1950-04-01',
            'journal': j,
            'volume': 182, 'issue': 4,
            'start_page': 13, 'end_page': 17,
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS'],
        }

        a = Article.objects.create(**a)
        auth = ArticleAuthorship(
            collaborator=cls.einstein, article=a, display_order=1)
        auth.save()
        cls.a = a

        # Create book object to test citation
        phila_negro = {
            "title": "The Philadelphia Negro",
            "short_title": "Philadelphia Negro",
            "slug": "philadelphia-negro",
            "pub_date": "1899-01-01",
            "status": PUBLICATION_STATUS['PUBLISHED_STATUS'],
            "publisher": "University of Pennsylvania Press",
            "place": "Philadelphia, Penn."
        }
        b = Book.objects.create(**phila_negro)
        auth = BookAuthorship(
            collaborator=cls.dubois, book=b, display_order=1)
        auth.save()
        cls.b = b

        # Create chapter object to test citation
        tenth = {
            "title": "The Talented Tenth",
            "short_title": "Talented Tenth", "slug": "talented-tenth",
            "book_title": ("The Negro Problem: A Series of Articles "
                           "by Representative American Negroes of To-day"),
            "status": PUBLICATION_STATUS["PUBLISHED_STATUS"],
            "pub_date": "1903-01-01",
            "start_page": 31, "end_page": 75,
            "publisher": "James Pott & Co.",
            "place": "New York"
        }
        c = Chapter.objects.create(**tenth)
        auth = ChapterAuthorship(
            collaborator=cls.dubois, chapter=c, display_order=1)
        auth.save()
        cls.washington = Collaborator.objects.create(
            first_name='Booker', last_name='Washington',
            middle_initial='T.', email='booker.t@example.com')
        chap_ed = ChapterEditorship(
            collaborator=cls.washington, chapter=c, display_order=1)
        chap_ed.save()
        cls.c = c

        r = {
            'title': 'States\' laws on race and color',
            'short_title': 'States\' laws',
            'slug': 'states-laws',
            'pub_date': '1950-01-01',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS'],
        }
        r = Report.objects.create(**r)
        auth = ReportAuthorship(
            collaborator = cls.murray, report=r, display_order=1)
        auth.save()
        cls.r = r

    def test_retrieve_csl_style(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        csl_dir = os.path.join(base_dir, 'cv', 'csl', 'apa.csl')
        self.assertEqual(
            Path(csl_dir),
            CSLStyle('apa').retrieve_csl_style())

    def test_citation_style(self):
        """Test that `cite()` method accepts only html and plain styles."""
        self.a.cite(style='html')
        self.a.cite(style='plain')
        with self.assertRaises(ValueError) as e:
            self.a.cite(style='tex')
            self.assertEqual(_('Citation style must be either \'html\' or'
                               ' \'plain\''), str(e))

    def test_article_citation(self):
        """Test proper citation returned for article instance."""
        self.assertHTMLEqual(
            ("Einstein, A. (1950). On the Generalized Theory of Gravitation. "
             "<i>Scientific American</i>, <i>182</i>(4), 13–17."),
            self.a.cite())

    def test_article_malformed_citation(self):
        """Test that citation does not fail without complete citation info."""
        self.a.start_page = ''
        self.a.end_page = ''
        self.assertHTMLEqual(
            ("Einstein, A. (1950). On the Generalized Theory of Gravitation. "
             "<i>Scientific American</i>, <i>182</i>(4)."),
            self.a.cite())
        self.a.volume = ''
        self.a.issue = ''
        self.assertHTMLEqual(
            ("Einstein, A. (1950). On the Generalized Theory of Gravitation. "
             "<i>Scientific American</i>."),
            self.a.cite())
        self.a.journal = None
        self.assertHTMLEqual(
            "Einstein, A. (1950). On the Generalized Theory of Gravitation. ",
            self.a.cite())

    def test_book_citation(self):
        """Test proper citation returned for book instance."""
        self.assertHTMLEqual(
            ("Du Bois, W. E. B. (1899). <i>The Philadelphia Negro</i>. "
             "Philadelphia, Penn.: University of Pennsylvania Press."),
            self.b.cite())

    def test_book_malformed_citation(self):
        """Test that cite() returns citation without complete info."""
        self.b.place = ''
        self.assertHTMLEqual(
            ("Du Bois, W. E. B. (1899). <i>The Philadelphia Negro</i>. "
             "University of Pennsylvania Press."),
            self.b.cite())
        self.b.publisher = ''
        self.assertHTMLEqual(
            "Du Bois, W. E. B. (1899). <i>The Philadelphia Negro</i>.",
            self.b.cite())
        self.b.pub_date = ''
        self.assertHTMLEqual(
            "Du Bois, W. E. B. (published). <i>The Philadelphia Negro</i>.",
            self.b.cite())

    def test_chapter_citation(self):
        self.assertHTMLEqual(
            ("Du Bois, W. E. B. (1903). The Talented Tenth. In B. T. "
             "Washington (Ed.), <i>The Negro Problem: A Series of Articles "
             "by Representative American Negroes of To-day</i>  "
             "(pp. 31–75). New York: James Pott & Co."),
            self.c.cite())

    def test_chapter_malformed_citation(self):
        self.c.publisher = ''
        self.c.place = ''
        self.assertHTMLEqual(
            ("Du Bois, W. E. B. (1903). The Talented Tenth. In B. T. "
             "Washington (Ed.), <i>The Negro Problem: A Series of Articles "
             "by Representative American Negroes of To-day</i>  "
             "(pp. 31–75)."),
            self.c.cite())
        self.c.start_page = ''
        self.c.end_page = ''
        self.assertHTMLEqual(
            ("Du Bois, W. E. B. (1903). The Talented Tenth. In B. T. "
             "Washington (Ed.), <i>The Negro Problem: A Series of Articles "
             "by Representative American Negroes of To-day</i> ."),
            self.c.cite())

    def test_chapter_fails_without_editorship(self):
        self.c.editorship.all().delete()
        self.c.save()
        try:
            self.c.cite()
        except CSLKeyError as e:
            self.assertEqual(CSLKeyError, type(e))
            self.assertEqual(
                'Cannot cite \'chapter\' when \'editorship\' is undefined',
                str(e))

    def test_report_citation(self):
        self.assertHTMLEqual(
            ("Murray, P. (1950). <i>States\' laws on race and color</i>."),
            self.r.cite())
