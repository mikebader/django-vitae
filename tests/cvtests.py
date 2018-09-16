from django.apps import apps 
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from cv.models import Collaborator
from cv.settings import INPREP_RANGE, INREVISION_RANGE, PUBLISHED_RANGE

class VitaePublicationTestCase(TestCase):
        def assess_status_values(self, a, value):
            """
            Test whether status flag fields are correct on create and update

            * ``is_published`` field should be True if status>=50 & <90,
            * ``is_inrevision`` field should be True if status>=20 & <50, and
            * ``is_inprep`` field should be True if status>0 & <20 on creation.
            """
            if PUBLISHED_RANGE.min <= a.status < PUBLISHED_RANGE.max:
                self.assertTrue(
                    a.is_published,
                    "The is_published field should be "
                    "True when `status` field equals %s" % value[0])
            else:
                self.assertFalse(
                    a.is_published,
                    _("The is_published field should be "
                      "False when `status` field equals %s") % value[0])
            if INREVISION_RANGE.min <= a.status < INREVISION_RANGE.max:
                self.assertTrue(
                    a.is_inrevision,
                    _("The is_inrevision field should be "
                      "True when `status` field equals %s") % value[0])
            else:
                self.assertFalse(
                    a.is_inrevision,
                    _("The is_inrevision field should be "
                      "False when `status` field equals %s") % value[0])
            if INPREP_RANGE.min <= a.status < INPREP_RANGE.max:
                self.assertTrue(
                    a.is_inprep,
                    _("The is_inprep field should be "
                      "True when `status` field equals %s") % value[0])
            else:
                self.assertFalse(
                    a.is_inprep,
                    _("The is_inprep field should be "
                      "False when `status` field equals %s") % value[0])

        def assertNextByStatus(self, penultimate, expected_final_slug):
            """
            Test that ``get_next_by_status()`` returns previous publication
            with stame status and returns DoesNotExist error if instance is
            the most recent publication with status.
            """
            (model, model_name) = (penultimate._meta.model,
                                   penultimate._meta.model_name)
            final = penultimate.get_next_by_status()
            self.assertEqual(final.slug, expected_final_slug)
            DoesNotExist = model.DoesNotExist
            self.assertRaisesMessage(
                DoesNotExist,
                _("There are no subsequent %ss with same status") %
                model_name.title(),
                final.get_next_by_status
            )

        def assertPreviousByStatus(self, second, expected_first_slug):
            """
            Test that ``get_previous_by_status()`` returns previous
            publication with stame status and returns DoesNotExist error if
            instance is the first recent publication with status.
            """
            (model, model_name) = (second._meta.model, second._meta.model_name)
            first = second.get_previous_by_status()
            self.assertEqual(first.slug, expected_first_slug)
            DoesNotExist = model.DoesNotExist
            self.assertRaisesMessage(
                DoesNotExist,
                _("There are no previous %ss with same status") %
                model_name.title(),
                first.get_previous_by_status
            )

        def assertNoNextPreviousByStatus(self, pub):
            model = type(pub)
            DoesNotExist = model.DoesNotExist
            self.assertRaisesMessage(
                DoesNotExist,
                _('%s must be in revision or publication status') %
                pub._meta.object_name,
                pub.get_next_by_status)
            self.assertRaisesMessage(
                DoesNotExist,
                _('%s must be in revision or publication status') %
                pub._meta.object_name,
                pub.get_previous_by_status)

        def assertAcceptsValidISBN(self, instance):
            try:
                isbns = {"isbn10": "0812215737",
                         "isbn10X": "014200068X",
                         "isbn10x": "014200068x",
                         "isbn13": "978-0812215731",
                         "isbn13grouped": "978-0-81-221573-1"}
                for k, isbn in isbns.items():
                    instance.isbn = isbn
                    instance.save()
                    instance.delete()
            except ValidationError:
                raise AssertionError('Valid ISBN values failed to save')

        def assertDoesNotAcceptInvalidISBN(self, instance):
            invalid_isbns = {"isbn11": "08122157372",
                             "isbnlet": "a081221573",
                             "isbn13": "123456789012X"}
            for k, isbn in invalid_isbns.items():
                instance.isbn = isbn
                try:
                    instance.save()
                    raise ValidationError("%s should not have been updated"
                                          "with invalid ISBN" % str(instance))
                except ValidationError:
                    self.assertRaisesMessage(ValidationError,
                                             _("Improperly formatted ISBN"))

        def assertDoesNotAcceptMalformedISBN(self, instance):
            malformed_isbns = {"transp_10": "0812217537",
                               "transp_13": "978-0812215371"}
            for k, isbn in malformed_isbns.items():
                instance.isbn = isbn
                try:
                    instance.save()
                    raise ValidationError("%s should not have been created"
                                          "with invalid ISBN" % str(instance))
                except ValidationError:
                    self.assertRaisesMessage(
                        ValidationError,
                        _("Inproper checksum digit for ISBN, "
                          "check that you entered the ISBN "
                          "correctly"))


class AuthorshipTestCase(TestCase):

    @classmethod
    def setUp(cls):
        cls.dubois = Collaborator.objects.create(
            first_name="William", last_name="Du Bois",
            middle_initial="E.B.", email="dubois@example.com")
        cls.dill = Collaborator.objects.create(
            first_name="Augustus", middle_initial="G.",
            last_name="Dill", email="dill@example.com")
        cls.einstein = Collaborator.objects.create(
            first_name="Albert", last_name="Einstein",
            email="ae@example.edu")
        cls.warner = Collaborator.objects.create(
            first_name="Yakko", last_name="Warner",
            email="yakko.warner@wbwatertower.com")
        cls.murray = Collaborator.objects.create(
            first_name="Pauli", last_name="Murray",
            email="pauli.murray@example.com")

    def assertAuthorshipLength(self, instance, num_authors):
        """Test that authorship set returns proper length of authors."""
        num_authors_found = len(instance.authorship.all())
        self.assertEqual(
            num_authors_found,
            num_authors,
            'Number of authors (%s) does not match num_authors given' %
            num_authors_found)

    def assertAuthorshipDisplayOrder(self, instance, authors):
        """Test that authorship set returns authors by ``display_order``."""
        authorships = instance.authorship.all()
        author_matches = [(str(authorship), str(author))
                          for authorship, author in zip(authorships, authors)]
        for author_match in author_matches:
            self.assertEqual(*author_match)

    def assertAuthorshipStudentStatus(self, instance, students, not_students):
        """Test that authorship set returns ``student_colleague`` values."""
        for student in students:
            author_test = Collaborator.objects.get(email=student)
            author = instance.authorship.get(collaborator=author_test.pk)
            self.assertIsInstance(author.student_colleague, int)
        for author in not_students:
            author_test = Collaborator.objects.get(email=author)
            author = instance.authorship.get(collaborator=author_test.pk)
            self.assertIsNone(author.student_colleague)
