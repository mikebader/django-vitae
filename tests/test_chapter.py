"""Tests for Django-CV Chapter model"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.settings import PUBLICATION_STATUS, STUDENT_LEVELS
from cv.models import Chapter, ChapterAuthorship, ChapterEditorship, \
    Collaborator

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase


# #######################################
# #  CHAPTERS                           #
# #######################################
@attr('chapter')
class ChapterTestCase(VitaePublicationTestCase, AuthorshipTestCase):
    """Run tests of Django-CV :class:`~cv.models.Book` model."""

    @classmethod
    def setUp(cls):
        super(ChapterTestCase, cls).setUp()
        cls.johnson = Collaborator.objects.create(
            first_name="Allen", last_name="Johnson",
            email="allen.johnson@example.com")
        cls.malone = Collaborator.objects.create(
            first_name="Dumas", last_name="Malone",
            email="dumas.malone@example.com")
        cls.fdouglass_fields = {
            'title': 'Douglass, Frederick',
            'short_title': 'Frederick Douglass',
            'slug': 'frederick-douglass', 'pub_date': '1930-01-01',
            'book_title': 'Dictionary of American Biography: Cushman – Eberle',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']}

        cls.freedom = Chapter.objects.create(
            title='My Evolving Program for Negro Freedom',
            short_title='Program for Negro Freedom',
            slug='program-negro-freedom', pub_date='1940-01-01',
            book_title='What the Negro Wants',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'])
        cls.logan = Collaborator.objects.create(
            first_name="Raymond", last_name="Logan",
            middle_initial="W.", email="logan@example.com")
        chap_auth = ChapterAuthorship(
            collaborator=cls.dubois, chapter=cls.freedom, display_order=1)
        chap_auth.save()
        chap_ed = ChapterEditorship(
            collaborator=cls.logan, chapter=cls.freedom, display_order=1)
        chap_ed.save()

        cls.ifre = Chapter.objects.create(
            title='The Nature of Intellectual Freedom',
            short_title='Intellectual Freedom', slug='intellectual-freedom',
            book_title='Speaking of Piece',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='1949-01-01')
        cls.gillmor = Collaborator.objects.create(
            first_name='Daniel', last_name='Gillmor',
            email='daniel.gilmore@example.com')
        chap_auth = ChapterAuthorship(
            collaborator=cls.dubois, chapter=cls.ifre, display_order=1)
        chap_auth.save()
        chap_ed = ChapterEditorship(
            collaborator=cls.gillmor, chapter=cls.ifre, display_order=1)
        chap_ed.save()

        cls.tenth = Chapter.objects.create(
            title='The Talented Tenth',
            short_title='Talented Tenth', slug='talented-tenth',
            book_title=('The Negro Problem: A Series of Articles'
                        'by Representative American Negroes of To-day'),
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='1903-01-01')
        cls.washington = Collaborator.objects.create(
            first_name='Booker', last_name='Washington',
            middle_initial='T.', email='booker.t@example.com')
        chap_auth = ChapterAuthorship(
            collaborator=cls.dubois, chapter=cls.tenth, display_order=1)
        chap_auth.save()
        chap_ed = ChapterEditorship(
            collaborator=cls.washington, chapter=cls.tenth, display_order=1)
        chap_ed.save()

    def add_chapter(self):
        fdouglass = Chapter.objects.create(**self.fdouglass_fields)
        chap_auth = ChapterAuthorship(
            collaborator=self.dubois, chapter=fdouglass, display_order=1)
        chap_auth.save()
        i = 1
        for editor in [self.johnson, self.malone]:
            chap_ed = ChapterEditorship(
                collaborator=editor, chapter=fdouglass, display_order=i)
            chap_ed.save()
            i += 1
        return fdouglass

    def add_student_author_to_chapter(self, chapter):
        """Add student collaborator as author to chapter."""
        ChapterAuthorship(
            chapter=chapter, collaborator=self.dill, display_order=2,
            student_colleague=STUDENT_LEVELS['DOCTORAL_STUDENT']).save()
        return chapter

    def test_chapter_str(self):
        chapter = Chapter.objects.get(slug='talented-tenth')
        self.assertEqual("Talented Tenth", str(chapter))

    def test_chapter_required_fields(self):
        req_fields = ['title', 'short_title', 'slug', 'status', 'book_title']
        for field in req_fields:
            chapter = self.fdouglass_fields.copy()
            chapter.pop(field)
            try:
                Chapter.objects.create(**chapter)
            except ValidationError as e:
                if field == 'status':
                    self.assertIn('This field cannot be null',
                                  str(e.error_dict[field][0]))
                else:
                    self.assertIn('This field cannot be blank',
                                  str(e.error_dict[field][0]))
            else:
                chapter.save()
                raise ValidationError(_('Chapter should not be saved without '
                                        'required field %s') % field)
                chapter.delete()

    def test_chapter_slug_unique(self):
        """Test chapter slug is unique."""
        Chapter.objects.create(**self.fdouglass_fields)
        try:
            Chapter.objects.create(**self.fdouglass_fields)
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Chapter with this Slug already exists',
                          str(e.error_dict['slug'][0]))

    def test_chapter_single_author(self):
        """Test that single authorship works correctly."""
        chapter = Chapter.objects.create(**self.fdouglass_fields)
        auth = ChapterAuthorship(
            chapter=chapter, collaborator=self.dubois, display_order=1)
        auth.save()
        self.assertAuthorshipLength(chapter, 1)

    def test_chapter_multiple_authors(self):
        """Test that multiple authors are saved correctly."""
        chapter = Chapter.objects.get(slug='talented-tenth')
        chapter = self.add_student_author_to_chapter(chapter)
        self.assertAuthorshipLength(chapter, 2)

    def test_chapter_display_order(self):
        """Test that authors appear in proper order."""
        chapter = Chapter.objects.get(slug='talented-tenth')
        chapter = self.add_student_author_to_chapter(chapter)
        authors = ['Du Bois, William E.B.', 'Dill, Augustus G.']
        self.assertAuthorshipDisplayOrder(chapter, authors)

    def test_chapter_authorship_student_collaboration(self):
        """Test student colleague status for chapter authorship."""
        chapter = Chapter.objects.get(slug='talented-tenth')
        chapter = self.add_student_author_to_chapter(chapter)
        self.assertAuthorshipStudentStatus(
            chapter, ['dill@example.com'], ['dubois@example.com'])

    def test_chapter_authorship_order_unique(self):
        """Test that display_order may not be repeated for a chapter."""
        chapter = Chapter.objects.get(slug='talented-tenth')
        auth = ChapterAuthorship(
            collaborator=self.dill, chapter=chapter, display_order=1)
        err_msg = ('Chapter authorship with this Chapter and '
                   'Display order already exists.')
        with self.assertRaisesMessage(ValidationError, err_msg):
            auth.save()

    def test_chapter_single_editor(self):
        chapter = Chapter.objects.create(**self.fdouglass_fields)
        ed = ChapterEditorship(
            chapter=chapter, collaborator=self.johnson, display_order=1)
        ed.save()
        num_eds_found = len(chapter.editorship.all())
        self.assertEqual(
            num_eds_found, 1,
            _('Number of editors (%s) does not match num_authors given') %
            num_eds_found)

    def test_chapter_multiple_editors(self):
        chapter = self.add_chapter()
        num_eds_found = len(chapter.editorship.all())
        self.assertEqual(
            num_eds_found, 2,
            _('Number of authors (%s) does not match num_authors given') %
            num_eds_found)

    def test_chapter_editorship_display_order(self):
        chapter = self.add_chapter()
        eds = ['Johnson, Allen', 'Malone, Dumas']
        editorships = chapter.editorship.all()
        ed_matches = [(str(editorship), str(editor))
                      for editorship, editor in zip(editorships, eds)]
        for ed_match in ed_matches:
            self.assertEqual(*ed_match)

    def test_chapter_editorship_order_repeated(self):
        chapter = Chapter.objects.get(slug='talented-tenth')
        ed = ChapterEditorship(
            collaborator=self.dill, chapter=chapter, display_order=1)
        err_msg = ('Chapter editorship with this Chapter and '
                   'Display order already exists.')
        with self.assertRaisesMessage(ValidationError, err_msg):
            ed.save()

    # test methoods
    # clean
    def test_chapter_isbn_validation(self):
        c = Chapter.objects.get(slug='talented-tenth')
        self.assertAcceptsValidISBN(c)
        self.assertDoesNotAcceptInvalidISBN(c)
        self.assertDoesNotAcceptMalformedISBN(c)

    # save
    def test_chapter_abstract_markdown(self):
        chapter = Chapter.objects.get(slug='talented-tenth')
        chapter.abstract = "Du Bois was *not* known for his **chapters**"
        chapter.save()
        self.assertEqual(chapter.abstract_html,
                         "<p>Du Bois was <em>not</em> known for "
                         "his <strong>chapters</strong></p>")

    def test_chapter_status_fields(self):
        """Test whether status flag fields are correct on create and update."""
        for value in Chapter._meta.get_field('status').choices:
            fields = self.fdouglass_fields.copy()
            fields['status'] = value[0]
            c = Chapter.objects.create(**fields)
            self.assess_status_values(c, value)
            c.delete()
        fields = self.fdouglass_fields.copy()
        c = Chapter.objects.create(**fields)
        for value in Chapter._meta.get_field('status').choices:
            c.status = value[0]
            c.save()
            self.assess_status_values(c, value)

    # get_absolute_url
    def test_chapter_get_absolute_url(self):
        """Test that instance returns correct url."""
        chapter = Chapter.objects.get(slug='talented-tenth')
        self.assertEqual("/chapters/talented-tenth/",
                         chapter.get_absolute_url())

    # custom methods
    def test_chapter_get_next_published_status(self):
        """Test that get_next_by_status() returns published chapters."""
        c = Chapter.objects.get(slug='program-negro-freedom')
        self.assertNextByStatus(c, 'intellectual-freedom')

    def test_chapter_get_previous_published_status(self):
        """Test that get_previous_by_status() returns published chapters."""
        c = Chapter.objects.get(slug='program-negro-freedom')
        self.assertPreviousByStatus(c, 'talented-tenth')

    def test_chapter_get_next_submitted_status(self):
        """Test that get_next_by_status() returns inrevision chapters."""
        for c in Chapter.objects.all():
            c.status = PUBLICATION_STATUS['SUBMITTED_STATUS']
            c.submission_date = c.pub_date
            c.save()
        c = Chapter.objects.get(slug='program-negro-freedom')
        self.assertNextByStatus(c, 'intellectual-freedom')

    def test_chapter_get_previous_submitted_status(self):
        """Test that get_previous_by_status() returns inrevision chapters."""
        for c in Chapter.objects.all():
            c.status = PUBLICATION_STATUS['SUBMITTED_STATUS']
            c.submission_date = c.pub_date
            c.save()
        c = Chapter.objects.get(slug='program-negro-freedom')
        self.assertPreviousByStatus(c, 'talented-tenth')

    def test_get_next_unpublished_statuses(self):
        """Test that get_next_previous_by_status() returns error for statuses
        that are not publish or inrevision.
        """
        for chapter in Chapter.objects.all():
            chapter.status = PUBLICATION_STATUS['INPREP_STATUS']
            self.assertNoNextPreviousByStatus(chapter)

