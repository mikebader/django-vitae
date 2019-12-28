# from django.apps import apps
from django.core.exceptions import ValidationError
# from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from tests.publications.pubs_tests import PublicationTestCase

from cv.models import Article
from cv.settings import PUBLICATION_STATUS, INPREP_RANGE, INREVISION_RANGE, \
    PUBLISHED_RANGE


@attr('article')
class ArticleTestCase(PublicationTestCase):

    def test_article_string(self):
        """Tests that model instance returns short title of article"""
        a = Article.objects.get(
            slug='gen-theory-gravitation')
        self.assertEqual(a.__str__(), 'Generalized Theory of Gravitation')

    def test_article_repr(self):
        """Tests that model repr method returns object type and short title"""
        a = Article.objects.get(
            slug='gen-theory-gravitation')
        self.assertEqual(
            a.__repr__(), '<Article: Generalized Theory of Gravitation>')

    def test_article_title_required(self):
        """Tests title is required to save object"""
        test_art = Article(short_title='Test', slug='test', status=1)
        try:
            test_art.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['title'][0]))

    def test_article_title_not_blank(self):
        """Tests that article title must not contain only space characters"""
        test_art = Article(title=' ', short_title=' ', slug='-', status=1)
        try:
            test_art.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Title must contain non-whitespace characters',
                          str(e.error_dict['title'][0]))

    def test_article_short_title_required(self):
        """Tests short_title is required to save object"""
        test_art = Article(title='Test', slug='test', status=1)
        try:
            test_art.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['short_title'][0]))

    def test_article_slug_required(self):
        """Tests slug field required to save object"""
        test_art = Article(title='Test', short_title='Test', status=1)
        try:
            test_art.save()
        except ValidationError as e:
            print(e.error_dict)
            self.assertEqual(ValidationError, type(e))
            self.assertIn('This field cannot be blank',
                          str(e.error_dict['slug'][0]))

    def test_article_slug_unique(self):
        """Tests that slug is unique in order to save object"""
        try:
            Article.objects.create(
                title='Quantum Theory Redux',
                short_title='Quantum Theory Redux',
                slug='quantum-theory',
                status=PUBLICATION_STATUS['PUBLISHED_STATUS'])
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertIn('Article with this Slug already exists',
                          str(e.error_dict['slug'][0]))

    def test_article_get_absolute_url(self):
        """Tests that article object returns URL containing slug."""
        q = Article.objects.get(slug="quantum-theory")
        self.assertEqual("/articles/quantum-theory/",
                         q.get_absolute_url())

    def test_article_cite(self):
        """Tests that object returns formatted citation."""
        article = Article.objects.get(slug='past-future-quantum-mechanics')
        self.assertHTMLEqual(
            'Einstein, A., Tolman, R. C., &amp; Podolsky, B. (1931). '
            'Knowledge of past and future in quantum mechanics. '
            '<i>Physical Review</i>, <i>37</i>, 780–781.',
            article.cite()
        )


@attr('article-rollback')
class ArticleRollbackTestCase(ArticleTestCase):

    @classmethod
    def setUp(cls):
        cls.art_base = Article(
            title='Base Article for Testing',
            short_title='Base Article',
            slug='base-article',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='2151-01-01'
        )
        cls.art_base.save()

        cls.art_next = Article(
            title='Next Article for Testing',
            short_title='Next Article',
            slug='next-article',
            status=cls.art_base.status,
            pub_date='2151-06-01'
        )
        cls.art_next.save()

        cls.art_prev = Article(
            title='Previous Article for Testing',
            short_title='Previous Article',
            slug='previous-article',
            status=cls.art_base.status,
            pub_date='2150-06-01'
        )
        cls.art_prev.save()

    def test_article_inprep_range(self):
        """Tests that article within 0 to 9 is set to being 'in prep'"""
        for i in PUBLICATION_STATUS:
            j = PUBLICATION_STATUS[i]
            if j in range(INPREP_RANGE.min, INPREP_RANGE.max):
                self.art_base.status = j
                self.art_base.save()
                self.assertTrue(
                    self.art_base.is_inprep,
                    _('Value %s should be classified as "inprep" status' % i))
            else:
                self.art_base.status = j
                self.art_base.save()
                self.assertFalse(
                    self.art_base.is_inprep,
                    _('Value %s should not be classified as '
                      '"inprep" status' % i)
                )

    def test_article_inrevision_range(self):
        """Tests that article within 20 to 49 is set to being 'in revision'"""
        for i in PUBLICATION_STATUS:
            j = PUBLICATION_STATUS[i]
            if j in range(INREVISION_RANGE.min, INREVISION_RANGE.max):
                self.art_base.status = j
                self.art_base.save()
                self.assertTrue(
                    self.art_base.is_inrevision,
                    _('Value %s should be classified as '
                      '"inrevision" status' % i)
                )
            else:
                self.art_base.status = j
                self.art_base.save()
                self.assertFalse(
                    self.art_base.is_inrevision,
                    _('Value %s should not be classified as '
                      '"inrevision" status' % i)
                )

    def test_article_published_range(self):
        """Tests that article within 50 to 89 is set to being 'in prep'"""
        for i in PUBLICATION_STATUS:
            j = PUBLICATION_STATUS[i]
            if j in range(PUBLISHED_RANGE.min, PUBLISHED_RANGE.max):
                self.art_base.status = j
                self.art_base.save()
                self.assertTrue(
                    self.art_base.is_published,
                    'Value %s should be classified as "published" status' % i)
            else:
                self.art_base.status = j
                self.art_base.save()
                self.assertFalse(
                    self.art_base.is_published,
                    'Value %s should not be classified as '
                    '"published" status' % i)

    def test_article_abstract_markdown_to_html(self):
        """Test markdown converstion of ``abstract`` saves HTML to
        ``abstract_html``."""
        self.art_base.status = PUBLICATION_STATUS['PUBLISHED_STATUS']
        self.art_base.abstract = "This is the **abstract**."
        self.art_base.save()
        self.assertHTMLEqual(self.art_base.abstract_html,
                             "<p>This is the <strong>abstract</strong>.</p>")

    def test_article_get_next_previous_by_status_submission_date(self):
        """Tests that articles in revision must have submission date"""
        article = Article.objects.get(slug='base-article')
        with self.assertRaises(
            ValueError,
            msg='Non-published articles need non-empty submission_date field'
        ):
            article.get_next_by_status()

    def test_article_next_previous_by_status_submitted(self):
        """Tests get_next_by_status() returns next submitted article."""
        next_decoy = Article(
            title='Decoy Next Article to Test Status',
            short_title='Next Article',
            slug='decoy-next-article',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='1951-01-27'
        )
        next_decoy.save()

        prev_decoy = Article(
            title='Decoy Previous Article to Test Status',
            short_title='Previous Article',
            slug='decoy-previous-article',
            status=PUBLICATION_STATUS['PUBLISHED_STATUS'],
            pub_date='1951-01-25'
        )
        prev_decoy.save()

        for article in Article.objects.filter(pub_date__gte='2150-01-01'):
            article.submission_date = article.pub_date
            article.save()
        article = Article.objects.get(slug='base-article')
        self.assertEqual(
            str(article.get_next_by_status()),
            'Next Article'
        )
        self.assertEqual(
            str(article.get_previous_by_status()),
            'Previous Article'
        )

    def test_article_next_previous_by_status_published(self):
        """Tests get_next_by_status() returns next published article."""
        next_decoy = Article(
            title='Decoy Next Article to Test Status',
            short_title='Next Article',
            slug='decoy-next-article',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='1951-01-27'
        )
        next_decoy.save()

        prev_decoy = Article(
            title='Decoy Previous Article to Test Status',
            short_title='Previous Article',
            slug='decoy-previous-article',
            status=PUBLICATION_STATUS['REVISE_STATUS'],
            pub_date='1951-01-25'
        )
        prev_decoy.save()

        article = Article.objects.get(slug='quantum-theory')
        self.assertEqual(
            str(article.get_next_by_status()),
            'Criticism of Unified Field Theory'
        )
        self.assertEqual(
            str(article.get_previous_by_status()),
            'Generalized Theory of Gravitation'
        )

    def test_article_next_previous_by_status_not_inprep(self):
        """Tests that get next by status does not work for inprep articles."""
        article = Article.objects.get(slug='base-article')
        article.status = 0
        article.save()
        try:
            article.get_next_by_status()
        except ValueError as e:
            print(e)
            self.assertIn('Article must be in revision or publication status',
                          str(e))
