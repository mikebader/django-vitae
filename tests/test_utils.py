from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr
from unittest import TestCase

from cv.utils import check_isbn
from cv.utils import retrieve_csl_style


@attr('utils')
class UtilsTest(TestCase):
    """
    Test class to check utility functions in Django-CV

    :class:`cv.tests.UtilsTest` uses Python :class:`py.unittest.TestCase`
    rather than Django subclass of ``TestCase`` because the utility
    functions should not rely on any Django-specific functionality
    (except for translation).
    """

    def test_check_isbn_function_well_formed(self):
        """Test that well-formed ISBNs pass check_isbn()."""
        real_isbn_13s = ['9780553418811', '9780143127536', '9780520271425',
                         '014200068X', '014200068x']
        real_isbn_10s = ['0553418831', '0143127535', '0520271424']
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

    def test_retrieve_style(self):
        ## Need to add basic csl file to be distributed with application and then test its existence here
        self.assertEqual(retrieve_csl_style('harvard1'), "/Users/bader/webdev/djangoapps/cv-dev/csl/harvard1.csl")
