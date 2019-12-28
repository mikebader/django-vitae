from django.test import TestCase

from cv.models import Article, ArticleAuthorship, Collaborator, Journal, \
    Discipline
from cv.settings import PUBLICATION_STATUS


class PublicationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Fills database for tests of publication models.

        This test case should only be used for data that do not modify the
        database.This test set up *should not* be used for tests that modify
        the database (e.g., those that create or delete model objects).
        """
        super(PublicationTestCase, cls).setUpTestData()

        cls.aut_einstein = Collaborator.objects.create(
            first_name="Albert", last_name="Einstein",
            email="ae@example.edu")
        cls.aut_laub = Collaborator.objects.create(
            first_name="Jakob", last_name="Laub",
            email="jl@example.edu")
        cls.aut_tolman = Collaborator.objects.create(
            first_name="Richard", last_name="Tolman",
            middle_initial="C.",
            email="rct@example.edu")
        cls.aut_podolsky = Collaborator.objects.create(
            first_name="Boris", last_name="Podolsky",
            email="bp@example.edu")
        # cls.dubois = Collaborator.objects.create(
        #     first_name="William", last_name="Du Bois",
        #     middle_initial="E.B.", email="dubois@example.com")
        # cls.dill = Collaborator.objects.create(
        #     first_name="Augustus", middle_initial="G.",
        #     last_name="Dill", email="dill@example.com")
        # cls.warner = Collaborator.objects.create(
        #     first_name="Yakko", last_name="Warner",
        #     email="yakko.warner@wbwatertower.com")
        # cls.murray = Collaborator.objects.create(
        #     first_name="Pauli", last_name="Murray",
        #     email="pauli.murray@example.com")

        cls.dsc_phys = Discipline.objects.create(name='Physics', slug='Physics')
        cls.jou_sciam = Journal.objects.create(title='Scientific American')
        cls.jou_annphys = Journal.objects.create(title='Annalen der Physik')
        cls.jou_physrev = Journal.objects.create(title='Physical Review')

        a1 = {
            'title': 'On the Fundamental Electromagnetic Equations '
                     'for Moving Bodies',
            'short_title': 'Fundemental Electromagnetic Equations',
            'slug': 'fundamental-electromagnetic-equations',
            'pub_date': '1909-01-19',
            'journal': cls.jou_annphys,
            'volume': 26, 'start_page': 532, 'end_page': 540,
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        a2 = {
            'title': 'Knowledge of past and future in quantum mechanics',
            'short_title': 'Past and Future in Quantum Mechanics',
            'slug': 'past-future-quantum-mechanics',
            'journal': cls.jou_physrev,
            'volume': 37, 'start_page': 780, 'end_page': 781,
            'pub_date': '1931-02-26',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        a3 = {
            'title': 'On the Generalized Theory of Gravitation',
            'short_title': 'Generalized Theory of Gravitation',
            'slug': 'gen-theory-gravitation',
            'pub_date': '1950-04-01',
            'journal': cls.jou_sciam,
            'volume': 182, 'issue': 4,
            'start_page': 13, 'end_page': 17,
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS'],
        }
        a4 = {
            'title': 'The Advent of Quantum Theory',
            'short_title': 'Quantum Theory',
            'slug': 'quantum-theory',
            'pub_date': '1951-01-26',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        a5 = {
            'title': 'A Comment on a Criticism of Unified Field Theory',
            'short_title': 'Criticism of Unified Field Theory',
            'slug': 'crit-unified-field-theory',
            'pub_date': '1953-11-12',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        a6 = {
            'title': 'Unified Theory of the Universe: Finding God\'s Dice',
            'short_title': 'Unified Theory',
            'slug': 'unified-theory',
            'status': PUBLICATION_STATUS['INPREP_STATUS']
        }

        # Create articles and add lead author
        for article in [a1, a2, a3, a4, a5, a6]:
            a = Article.objects.create(**article)
            authorship = ArticleAuthorship(
                collaborator=cls.aut_einstein, article=a, display_order=1)
            authorship.save()

        # Add coauthors
        auth = ArticleAuthorship(
            article=Article.objects.get(slug=a1['slug']),
            collaborator=cls.aut_laub,
            display_order=2)
        auth.save()

        for i, x in enumerate([cls.aut_tolman, cls.aut_podolsky]):
            auth = ArticleAuthorship(
                article=Article.objects.get(slug=a2['slug']),
                collaborator=x,
                display_order=i + 2)
            auth.save()
