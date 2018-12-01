from django.core.exceptions import ValidationError
# from django.db import connection
# from django.db.models.base import ModelBase
from django.test import TestCase

from nose.plugins.attrib import attr

from cv.models import Collaborator, Discipline, Journal


@attr('base')
class BaseModelsTestCase(TestCase):
    """Test non-abstract models in base.py."""

    def test_collaborator(self):
        """Collaborator creation and string representation."""
        Collaborator.objects.create(
            first_name='Yakko', last_name='Warner',
            email='yakko@warnerbrostower.com')
        self.assertEqual(str(Collaborator.objects.all().first()),
                         'Warner, Yakko')

    def test_collaborator_ordering(self):
        """Ordering should be alphabetical by last name then first name."""
        Collaborator.objects.create(
            first_name='Yakko', last_name='Warner',
            email='yakko@warnerbrostower.com')
        Collaborator.objects.create(
            first_name='Wakko', last_name='Warner',
            email='wakko@warnerbrostower.com')
        Collaborator.objects.create(
            first_name='Albert', last_name='Einstein',
            email='einstein@example.com')
        collabs = [str(collab) for collab in Collaborator.objects.all()]
        self.assertEqual(
            ['Einstein, Albert', 'Warner, Wakko', 'Warner, Yakko'],
            collabs)

    def test_discipline(self):
        """Discipline string should be name and should have unique slug."""
        discipline = Discipline.objects.create(
            name='Sociology', slug='soci')
        self.assertEqual(str(discipline), 'Sociology')
        with self.assertRaises(ValidationError) as err:
            Discipline.objects.create(
                name='Social Work', slug='soci')
        e = err.exception
        self.assertTrue('slug' in e.error_dict.keys())
        self.assertRegex(
            e.message_dict['slug'][0],
            'already exists.$'
        )

    def test_discipline_ordering(self):
        """Disciplines should be ordered alphabetically."""
        Discipline.objects.create(
            name='Sociology', slug='sociology')
        Discipline.objects.create(
            name='Economics', slug='economics')
        disciplines = [str(d) for d in Discipline.objects.all()]
        self.assertEqual(disciplines, ['Economics', 'Sociology'])

    def test_journal(self):
        """Journal string should be title."""
        journal = Journal.objects.create(
            title='A Journal of Science')
        self.assertEqual(str(journal), 'A Journal of Science')

    def test_journal_ordering(self):
        """Order journals alphabetically ignoring articles."""
        Journal.objects.create(title="A Journal of Science")
        Journal.objects.create(title="American Journal of Science")
        journals = [str(j) for j in Journal.objects.all()]
        self.assertEqual(
            journals,
            ['American Journal of Science', 'A Journal of Science'])





