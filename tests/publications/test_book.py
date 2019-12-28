from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from tests.publications.pubs_tests import PublicationTestCase

from cv.models import Book
from cv.settings import PUBLICATION_STATUS, INPREP_RANGE, PUBLISHED_RANGE
from cv.utils import ISBNError


class BookBaseTestCase(PublicationTestCase):

    def test_book_string(self):
        """Tests that model instance returns short title of book"""
        a = Book.objects.get(
            slug='philadelphia-negro')
        self.assertEqual(a.__str__(), 'Philadelphia Negro')

    def test_book_repr(self):
        """Tests that model repr method returns object type and short title"""
        b = Book.objects.get(slug='philadelphia-negro')
        self.assertEqual(
            b.__repr__(), '<Book: Philadelphia Negro>')

    def test_book_title_required(self):
        """Tests title is required to save object"""
        test_book = Book(short_title='Test', slug='test', status=1)
        try:
            test_book.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['title'][0]))

    def test_book_title_not_blank(self):
        """Tests that book title must not contain only space characters"""
        test_book = Book(title=' ', short_title=' ', slug='-', status=1)
        try:
            test_book.save()
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Title must contain non-whitespace characters',
                          str(e.error_dict['title'][0]))

    def test_book_short_title_required(self):
        """Tests short_title is required to save object"""
        test_book = Book(title='Test', slug='test', status=1)
        try:
            test_book.save()
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['short_title'][0]))

    def test_book_slug_required(self):
        """Tests slug field required to save object"""
        test_book = Book(title='Test', short_title='Test', status=1)
        try:
            test_book.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['slug'][0]))

    def test_book_slug_unique(self):
        """Tests that slug is unique in order to save object"""
        try:
            Book.objects.create(
                title='The Philadelphia Negro Redux',
                short_title='Philadelphia Negro Redux',
                slug='philadelphia-negro',
                status=PUBLICATION_STATUS['PUBLISHED_STATUS'])
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Book with this Slug already exists',
                          str(e.error_dict['slug'][0]))

    def test_book_get_absolute_url(self):
        """Tests that book object returns URL containing slug."""
        b = Book.objects.get(slug='philadelphia-negro')
        self.assertEqual('/books/philadelphia-negro/',
                         b.get_absolute_url())

    def test_book_cite(self):
        """Tests that book returns formatted citation."""
        book = Book.objects.get(slug='philadelphia-negro')
        self.assertHTMLEqual(
            'Du Bois, W. E. B. (1899). <i>The Philadelphia Negro</i>. '
            'Philadelphia, Pennsylvania: University of Pennsylvania Press.',
            book.cite()
        )

    def test_book_edition_ordering(self):
        """Tests that book editions are returned by reverse pub date."""
        book = Book.objects.get(slug='philadelphia-negro')
        eds = ['1996 edition', '1st']
        editions = book.get_editions()
        for ed, edition in zip(eds, editions):
            self.assertEqual(ed, edition.edition)


@attr('book')
class BookTestCase(BookBaseTestCase):

    @classmethod
    def setUp(cls):
        cls.book_base = Book(
            title='Base Book for Testing',
            short_title='Base book',
            slug='base-book',
            place='New York',
            publisher='Publisher',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='2151-01-01'
        )
        cls.book_base.save()

        cls.book_next = Book(
            title='Next Book for Testing',
            short_title='Next Book',
            slug='next-book',
            place='New York',
            publisher='Publisher',
            status=cls.book_base.status,
            pub_date='2151-06-01'
        )
        cls.book_next.save()

        cls.book_prev = Book(
            title='Previous Book for Testing',
            short_title='Previous Book',
            slug='previous-book',
            place='New York',
            publisher='Publisher',
            status=cls.book_base.status,
            pub_date='2150-06-01'
        )
        cls.book_prev.save()

    def test_book_inprep_range(self):
        """Tests that book within 0 to 9 is set to being 'in prep'"""
        for i in PUBLICATION_STATUS:
            j = PUBLICATION_STATUS[i]
            if j in range(INPREP_RANGE.min, INPREP_RANGE.max):
                self.book_base.status = j
                self.book_base.save()
                self.assertTrue(
                    self.book_base.is_inprep,
                    _('Value %s should be classified as "inprep" status' % i))
            else:
                self.book_base.status = j
                self.book_base.save()
                self.assertFalse(
                    self.book_base.is_inprep,
                    _('Value %s should not be classified as '
                      '"inprep" status' % i)
                )

    def test_book_published_range(self):
        """Tests that book within 50 to 89 is set to being 'in prep'"""
        for i in PUBLICATION_STATUS:
            j = PUBLICATION_STATUS[i]
            if j in range(PUBLISHED_RANGE.min, PUBLISHED_RANGE.max):
                self.book_base.status = j
                self.book_base.save()
                self.assertTrue(
                    self.book_base.is_published,
                    'Value %s should be classified as "published" status' % i)
            else:
                self.book_base.status = j
                self.book_base.save()
                self.assertFalse(
                    self.book_base.is_published,
                    'Value %s should not be classified as '
                    '"published" status' % i)

    def test_book_abstract_markdown_to_html(self):
        """Test markdown converstion of ``abstract`` saves HTML to
        ``abstract_html``."""
        self.book_base.status = PUBLICATION_STATUS['PUBLISHED_STATUS']
        self.book_base.abstract = "This is the **abstract**."
        self.book_base.save()
        self.assertHTMLEqual(self.book_base.abstract_html,
                             "<p>This is the <strong>abstract</strong>.</p>")

    def test_book_get_next_previous_by_status_submission_date(self):
        """Tests that articles in revision must have submission date"""
        book = Book.objects.get(slug='base-book')
        with self.assertRaises(
            ValueError,
            msg='Non-published articles need non-empty submission_date field'
        ):
            book.get_next_by_status()

    def test_article_next_previous_by_status_submitted(self):
        """Tests get_next_by_status() returns next submitted book."""
        next_decoy = Book(
            title='Decoy Next Book for Testing',
            short_title='Decoy Next Book',
            slug='decoy-next-book',
            place='New York',
            publisher='Publisher',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='2151-06-01'
        )
        next_decoy.save()

        prev_decoy = Book(
            title='Decoy Previous Book for Testing',
            short_title='Decoy Previous Book',
            slug='decoy-previous-book',
            place='New York',
            publisher='Publisher',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='2151-01-25'
        )
        prev_decoy.save()

        for book in Book.objects.filter(pub_date__gte='2150-01-01'):
            book.submission_date = book.pub_date
            book.save()
        book = Book.objects.get(slug='base-book')
        self.assertEqual(
            str(book.get_next_by_status()),
            'Next Book',
            'Get next object by status failed'
        )
        self.assertEqual(
            str(book.get_previous_by_status()),
            'Previous Book',
            'Get previous by status failed'
        )

    def test_book_next_previous_by_status_published(self):
        """Tests get_next_by_status() returns next published book."""
        next_decoy = Book(
            title='Decoy Next Book for Testing',
            short_title='Decoy Next Book',
            slug='decoy-next-book',
            place='New York',
            publisher='Publisher',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='1902-01-01'
        )
        next_decoy.save()

        prev_decoy = Book(
            title='Decoy Previous Book for Testing',
            short_title='Decoy Previous Book',
            slug='decoy-previous-book',
            place='New York',
            publisher='Publisher',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='1904-01-01'
        )
        prev_decoy.save()

        book = Book.objects.get(slug='souls-black-folk')
        self.assertEqual(
            str(book.get_next_by_status()),
            'Black Reconstruction'
        )
        self.assertEqual(
            str(book.get_previous_by_status()),
            'Philadelphia Negro'
        )

    def test_book_next_previous_by_status_not_inprep(self):
        """Tests that get next by status does not work for inprep books."""
        book = Book.objects.get(slug='base-book')
        book.status = 0
        book.save()
        try:
            book.get_next_by_status()
        except ValueError as e:
            self.assertIn('Book must be in revision or publication status',
                          str(e))

    def test_book_malformed_isbn(self):
        """Tests book object won't save with incorrectly formatted ISBN."""
        book = Book.objects.get(slug='souls-black-folk')
        book.isbn = '12345678'  # Incorrect format
        try:
            book.save()
        except ISBNError as e:
            self.assertEqual(_('Improperly formatted ISBN'), str(e))

        book.isbn = '978-0140189981'  # Bad checksum
        try:
            book.save()
        except ISBNError as e:
            self.assertEqual(
                _('Inproper checksum digit for ISBN, check '
                  'that you entered the ISBN correctly'),
                str(e)
            )

    def test_book_add_edition(self):
        """Tests method on books to add edition."""
        book = Book.objects.get(slug='souls-black-folk')
        book.add_edition(edition='Reissued')
        self.assertEqual(len(book.get_editions()), 1)

    def test_book_add_edition_requires_edition_kwarg(self):
        """Tests that add_edition requires edition kwarg."""
        book = Book.objects.get(slug='souls-black-folk')
        with self.assertRaises(TypeError):
            book.add_edition(_('Edition name in positional argument'))
        try:
            book.add_edition(isbn='978-0140189988')
        except ValidationError as e:
            self.assertIn(_('The field "edition" cannot be blank'), e)

    def test_book_edition_malformed_isbn(self):
        book = Book.objects.get(slug='souls-black-folk')
        ed = {
            'book': book,
            'isbn': '12345678',
            'edition': 'Malformed ISBN Edition'
        }
        try:
            book.add_edition(**ed)
        except ISBNError as e:
            self.assertEqual(_('Improperly formatted ISBN'), str(e))

        ed['isbn'] = '978-0140189981'
        try:
            book.add_edition(**ed)
        except ISBNError as e:
            self.assertEqual(
                _('Inproper checksum digit for ISBN, check '
                  'that you entered the ISBN correctly'),
                str(e)
            )
