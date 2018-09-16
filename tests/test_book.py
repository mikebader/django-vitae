"""Tests for Django-CV Book model"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.settings import PUBLICATION_STATUS, STUDENT_LEVELS
from cv.models import Book, BookAuthorship, BookEdition, Collaborator

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase


@attr('book')
class BookTestCase(VitaePublicationTestCase, AuthorshipTestCase):
    """
    Run tests of Django-CV :class:`~cv.models.Book` model.
    """

    @classmethod
    def setUp(cls):
        super(BookTestCase, cls).setUp()
        def set_up_books(cls):
            cls.phila_negro = {
                "title": "The Philadelphia Negro",
                "short_title": "Philadelphia Negro",
                "slug": "philadelphia-negro",
                "pub_date": "1899-01-01",
                "status": PUBLICATION_STATUS['PUBLISHED_STATUS']
            }

            cls.first_ed = {
                "edition": "1st",
                "pub_date": "1899-01-01",
                "publisher": "University of Pennsylvania Press"
            }
            cls.second_ed = {
                "edition": "1996 edition",
                "pub_date": "1996-01-01",
                "publisher": "University of Pennsylvania Press"
            }
            cls.souls = {
                "title": "The Souls of Black Folk",
                "short_title": "Souls of Black Folk",
                "slug": "souls-black-folk",
                "pub_date": "1903-01-01",
                "status": PUBLICATION_STATUS['PUBLISHED_STATUS']
            }
            souls = Book.objects.create(**cls.souls)
            cls.reconst = {
                "title": "Black Reconstruction in America: An Essay "
                         "Toward a History of the Part Which Black Folk "
                         "Played in the Attempt to Reconstruct Democracy "
                         "in America, 1860–1880",
                "short_title": "Black Reconstruction in America",
                "slug": "black-reconstruction-america",
                "pub_date": "1935-01-01",
                "status": PUBLICATION_STATUS['PUBLISHED_STATUS']
            }
            reconst = Book.objects.create(**cls.reconst)
            cls.africa = {
                "title": "Africa, its Place in Modern History",
                "short_title": "Africa",
                "slug": "africa",
                "submission_date": "1934-01-01",
                "status": PUBLICATION_STATUS['INPREP_STATUS']
            }
            africa = Book.objects.create(**cls.africa)
            for book in [souls, reconst, africa]:
                dubois = Collaborator.objects.get(last_name='Du Bois')
                BookAuthorship(
                    book=book, collaborator=dubois, display_order=1).save()
        set_up_books(cls)

    def unpublish_books(self):
        for book in Book.published.all():
            book.status = 20
            book.submission_date = book.pub_date
            book.pub_date = None
            book.save()

    def add_student_author_to_book(self, book):
        """Add student collaborator as author to book."""
        dill = Collaborator.objects.get(last_name='Dill')
        BookAuthorship(
            book=book, collaborator=dill, display_order=2,
            student_colleague=STUDENT_LEVELS['DOCTORAL_STUDENT']).save()
        return book

    def test_book_required_fields(self):
        """Tests that model cannot be saved with required fields being null."""
        for field in ["title", "short_title", "slug", "status"]:
            book = self.phila_negro.copy()
            book.pop(field)
            try:
                Book.objects.create(**book)
            except ValidationError as e:
                self.assertEqual(ValidationError, type(e))
                self.assertTrue(field in e.error_dict.keys())
                if field == "status":
                    self.assertIn('This field cannot be null',
                                  str(e.error_dict[field][0]))
                else:
                    self.assertIn('This field cannot be blank',
                                  str(e.error_dict[field][0]))

    def test_book_slug_unique(self):
        """Test book slug is unique."""
        Book.objects.create(**self.phila_negro)
        try:
            Book.objects.create(**self.phila_negro)
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Book with this Slug already exists',
                          str(e.error_dict['slug'][0]))

    def test_book_str(self):
        """Tests that string representation is the short_title."""
        book = Book.objects.create(**self.phila_negro)
        self.assertEqual(str(book), "Philadelphia Negro")

    def test_book_single_author(self):
        """Test that single authorship works correctly"""
        book = Book.objects.create(**self.phila_negro)
        auth = Collaborator.objects.get(last_name='Du Bois')
        book_auth = BookAuthorship(
            book=book, collaborator=auth, display_order=1)
        book_auth.save()
        self.assertAuthorshipLength(book, 1)

    def test_book_multiple_authors(self):
        """Test that multiple authorship works correctly."""
        book = Book.objects.get(slug='souls-black-folk')
        book = self.add_student_author_to_book(book)
        self.assertAuthorshipLength(book, 2)

    def test_book_display_order(self):
        """Test that authors appear in proper order"""
        book = Book.objects.get(slug='souls-black-folk')
        book = self.add_student_author_to_book(book)
        authors = ['Du Bois, William E.B.', 'Dill, Augustus G.']
        self.assertAuthorshipDisplayOrder(book, authors)

    def test_book_authorship_student_collaboration(self):
        """Test student colleague status for book authorship."""
        book = Book.objects.get(slug='souls-black-folk')
        book = self.add_student_author_to_book(book)
        self.assertAuthorshipStudentStatus(
            book, ['dill@example.com'], ['dubois@example.com'])

    # Test internal methods
    # clean
    def test_book_isbn_field(self):
        """Test ISBN against regular expression validator"""
        b = Book.objects.get(slug='souls-black-folk')
        self.assertAcceptsValidISBN(b)
        self.assertDoesNotAcceptInvalidISBN(b)
        self.assertDoesNotAcceptMalformedISBN(b)

    # save
    def test_book_abstract_markdown(self):
        """Test whether Markdown conversion of abstract
         happens correctly"""
        book = Book.objects.get(slug='souls-black-folk')
        book.abstract = "*The Souls of Black Folk* is a **seminal** text."
        book.save()
        self.assertEqual(book.abstract_html,
                         "<p><em>The Souls of Black Folk</em> "
                         "is a <strong>seminal</strong> text.</p>")

    def test_book_set_status_field_method(self):
        """Test whether status flag fields are correct on create and update"""
        for value in Book._meta.get_field('status').choices:
            fields = self.phila_negro.copy()
            fields['status'] = value[0]
            b = Book.objects.create(**fields)
            self.assess_status_values(b, value)
            b.delete()
        fields = self.phila_negro.copy()
        b = Book.objects.create(**fields)
        for value in Book._meta.get_field('status').choices:
            b.status = value[0]
            b.save()
            self.assess_status_values(b, value)

    # get_absolute_url
    def test_book_get_absolute_url(self):
        """Test that instance returns correct url."""
        book = Book.objects.get(slug='souls-black-folk')
        self.assertEqual("/books/souls-black-folk/",
                         book.get_absolute_url())

    # Book Editions
    def test_book_editions_required_fields(self):
        """Test that book cannot be saved without required fields."""
        req_fields = ['book', 'edition']
        book = Book.objects.create(**self.phila_negro)
        all_fields = self.first_ed.copy()
        all_fields['book'] = book
        for field in all_fields:
            ed_fields = all_fields.copy()
            ed_fields.pop(field)
            edition = BookEdition(**ed_fields)
            if field in req_fields:
                try:
                    edition.save()
                except ValidationError as e:
                    self.assertTrue(field in e.error_dict.keys())
                    if field == 'book':
                        self.assertIn('This field cannot be null',
                                      str(e.error_dict[field][0]))
                    else:
                        self.assertIn('This field cannot be blank',
                                      str(e.error_dict[field][0]))
            else:
                edition.save()
                edition.delete()

    def test_book_add_edition(self):
        """Tests method adding editions to book instance."""
        book = Book.objects.create(**self.phila_negro)
        book.add_edition(**self.first_ed)
        self.first_ed.pop('edition')
        with self.assertRaises(ValidationError) as e:
            book.add_edition(**self.first_ed)
            self.assertEqual(
                _("The field 'edition' cannot be blank"), e.msg)

    def test_book_get_editions(self):
        """Tests get_editions() returns editions related to book instance."""
        info = self.phila_negro
        book = Book.objects.create(**info)
        book.save()
        self.assertEqual(len(book.get_editions()), 0)
        first_ed = self.first_ed.copy()
        second_ed = self.second_ed.copy()
        for edition in [first_ed, second_ed]:
            edition["book"] = book
            book_ed = BookEdition.objects.create(**edition)
            book_ed.save()
        self.assertEqual(len(book.get_editions()), 2)

    # Test Custom Methods
    def test_book_get_next_published_status(self):
        """Test that get_next_by_status() returns published articles."""
        b = Book.objects.get(slug='souls-black-folk')
        self.assertNextByStatus(b, 'black-reconstruction-america')

    def test_get_previous_published_status(self):
        """Test that get_previous_by_status() returns published articles."""
        Book.objects.create(**self.phila_negro)
        b = Book.objects.get(slug='souls-black-folk')
        self.assertPreviousByStatus(b, 'philadelphia-negro')

    def test_get_next_submitted_status(self):
        """Test that get_next_by_status() returns submimtted articles."""
        Book.objects.create(**self.phila_negro)
        self.unpublish_books()
        b = Book.objects.get(slug='souls-black-folk')
        self.assertNextByStatus(b, 'black-reconstruction-america')

    def test_get_previous_submitted_status(self):
        """Test that get_previous_by_status() returns submitted books."""
        Book.objects.create(**self.phila_negro)
        self.unpublish_books()
        b = Book.objects.get(slug='souls-black-folk')
        self.assertPreviousByStatus(b, 'philadelphia-negro')

    def test_get_next_unpublished_statuses(self):
        """Test that get_next_previous_by_status() returns error for statuses
        that are not publish or inrevision.
        """
        for book in Book.objects.all():
            book.status = PUBLICATION_STATUS['INPREP_STATUS']
            self.assertNoNextPreviousByStatus(book)
