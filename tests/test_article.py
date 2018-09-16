"""Tests for Django-CV Article model"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from nose.plugins.attrib import attr

from cv.settings import PUBLICATION_STATUS, STUDENT_LEVELS
from cv.models import Article, ArticleAuthorship, Collaborator

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase

#######################################
#  ARTICLES                           #
#######################################
@attr('article')
class ArticleTestCase(VitaePublicationTestCase, AuthorshipTestCase):
    """
    Run tests of Django-CV :class:`~cv.models.Article` model.
    """

    @classmethod
    def setUp(cls):
        """Set up data to run tests on :class:`~cv.models.Article` model."""
        super(ArticleTestCase, cls).setUp()

        g = {
            'title': 'On the Generalized Theory of Gravitation',
            'short_title': 'Generalized Theory of Gravitation',
            'slug': 'gen-theory-gravitation',
            'pub_date': '1950-04-01',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        q = {
            'title': 'The Advent of Quantum Theory',
            'short_title': 'Quantum Theory',
            'slug': 'quantum-theory',
            'pub_date': '1951-01-26',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }
        u = {
            'title': 'A Comment on a Criticism of Unified Field Theory',
            'short_title': 'Criticism of Unified Field Theory',
            'slug': 'crit-unified-field-theory',
            'pub_date': '1953-11-12',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }

        for article in [g, q, u]:
            a = Article.objects.create(**article)
            authorship = ArticleAuthorship(
                collaborator=cls.einstein, article=a, display_order=1)
            authorship.save()


        cls.single_article_inprep_req_fields = {
            'title': 'Unified Field Theory Discovered',
            'short_title': 'Unified Field Theory',
            'slug': 'unified-field-theory',
            'status': PUBLICATION_STATUS['INPREP_STATUS']
        }

        cls.single_article_resting_req_fields = {
            'title': 'Zum kosmologischen Problem.',
            'short_title': 'Cosmological Problem',
            'slug': 'cosmological-problem',
            'status': PUBLICATION_STATUS['RESTING_STATUS']
        }

        cls.all_new_articles = [
            cls.single_article_inprep_req_fields,
            cls.single_article_resting_req_fields,
        ]

    def unpublish_articles(self):
        for article in Article.published.all():
            article.status = 20
            article.submission_date = article.pub_date
            article.pub_date = None
            article.save()

    def test_article_string(self):
        """Tests that model returns short title of article as string"""
        a = Article.objects.get(
            short_title="Generalized Theory of Gravitation")
        self.assertEqual(a.__str__(), "Generalized Theory of Gravitation")

    # Test Required Fields on Article Model
    def test_article_status_cannot_be_null(self):
        """Tests that model cannot be saved with 'status' field being null."""
        article_req_fields = self.single_article_inprep_req_fields.copy()
        article_req_fields.pop('status')
        try:
            Article.objects.create(**article_req_fields)
        except ValidationError as e:
            self.assertEqual(ValidationError, type(e))
            self.assertTrue('status' in e.error_dict.keys())
            self.assertIn('This field cannot be null',
                          str(e.error_dict['status'][0]))

    def test_article_required_fields(self):
        """Tests that model cannot be saved with required fields being null."""
        req_fields = self.single_article_inprep_req_fields.copy()
        req_fields.pop('status')
        for k in req_fields.keys():
            test_dict = self.single_article_inprep_req_fields.copy()
            test_dict.pop(k)
            try:
                Article.objects.create(**test_dict)
            except ValidationError as e:
                self.assertEqual(ValidationError, type(e))
                self.assertIn('This field cannot be blank',
                              str(e.error_dict[k][0]))

    def test_article_slug_unique(self):
        """Test article slug is unique."""
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

    # Test Model Save Method
    def test_article_set_status_field_method(self):
        """Test whether status flag fields are correct on create and update"""
        fields = self.single_article_inprep_req_fields.copy()
        for value in Article._meta.get_field('status').choices:
            fields['status'] = value[0]
            a = Article.objects.create(**fields)
            self.assess_status_values(a, value)
            a.delete()
        a = Article.objects.create(**self.single_article_resting_req_fields)
        for value in Article._meta.get_field('status').choices:
            a.status = value[0]
            a.save()
            self.assess_status_values(a, value)

    def test_article_abstract_markdown_to_html(self):
        """Test markdown converstion of ``abstract`` saves HTML to
        ``abstract_html``."""
        a = Article(**self.single_article_inprep_req_fields)
        a.abstract = "This is the **abstract**."
        a.save()
        self.assertHTMLEqual(a.abstract_html,
                             "<p>This is the <strong>abstract</strong>.</p>")

    # Test Managers
    def test_get_inprep_articles(self):
        """Test that ``inprep`` manager returns only status==0"""
        self.assertEqual(len(Article.inprep.all()), 0)
        for fields in self.all_new_articles:
            Article.objects.create(**fields)
        self.assertEqual(len(Article.inprep.all()), 1)

    def test_revise_article_manager(self):
        """Test that ``revise`` manager returns only status>0 and <50"""
        for fields in self.all_new_articles:
            Article.objects.create(**fields)
        self.assertEqual(len(Article.revise.all()), 0)
        a = Article.objects.get(slug="unified-field-theory")
        a.status = PUBLICATION_STATUS['REVISE_STATUS']
        a.save()
        self.assertEqual(len(Article.revise.all()), 1)
        # a.status = PUBLICATION_STATUS['FORTHCOMING_STATUS']
        # a.pub_date, a.submission_date = ("1957-04-18", None)
        # a.save()
        # self.assertEqual(len(Article.revise.all()), 0)

    def test_published_article_manager(self):
        """Test that ``published`` manager returns only status>=50 & <99"""
        # for fieldset in self.all_new_articles:
        #     Article.objects.create(**fieldset)
        self.assertEqual(len(Article.published.all()), 3)
        # a = Article.objects.get(slug="unified-field-theory")
        # a.status = PUBLICATION_STATUS['PUBLISHED_STATUS']
        # a.pub_date = "1957-04-18"
        # a.save()
        # print(Article.published.all())
        # self.assertEqual(len(Article.published.all()), 4)

    # Test Built-in Methods
    def test_get_absolute_url(self):
        q = Article.objects.get(slug="quantum-theory")
        self.assertEqual("/articles/quantum-theory/",
                         q.get_absolute_url())

    # Test Custom Methods
    def test_get_next_published_status(self):
        """Test that ``get_next_by_status()`` returns published articles."""
        a = Article.objects.get(slug='quantum-theory')
        self.assertNextByStatus(a, 'crit-unified-field-theory')

    def test_get_previous_published_status(self):
        """
        Test that ``get_previous_by_status()`` returns published articles.
        """
        a = Article.objects.get(slug='quantum-theory')
        self.assertPreviousByStatus(a, 'gen-theory-gravitation')

    def test_get_next_submitted_status(self):
        """Test that ``get_next_by_status()`` returns submimtted articles."""
        self.unpublish_articles()
        a = Article.objects.get(slug='quantum-theory')
        self.assertNextByStatus(a, 'crit-unified-field-theory')

    def test_get_previous_submitted_status(self):
        """
        Test that ``get_previous_by_status()`` returns submitted articles.
        """
        self.unpublish_articles()
        a = Article.objects.get(slug='quantum-theory')
        self.assertPreviousByStatus(a, 'gen-theory-gravitation')

    def test_get_next_unpublished_statuses(self):
        """Test that ``get_next_previous_by_status()`` returns error for statuses 
        that are not publish or inrevision.
        """
        for fields in self.all_new_articles:
            a = Article.objects.create(**fields)
            self.assertNoNextPreviousByStatus(a)

    def test_get_next_previous_wrong_direction(self):
        """Test that ``get_next_previous_by_status()`` returns error for 
        direction other than 'previous' or 'next'."""
        a = Article.objects.all().first()
        with self.assertRaisesMessage(SyntaxError,
              "'direc' must be 'previous' or 'next'"):
            a.get_next_previous_by_status("subsequent")

    def test_article_authorship_length(self):
        """Test accuracy of the length of article authorship set."""
        a = Article.objects.get(slug='quantum-theory')
        self.assertAuthorshipLength(a, 1)

    def test_article_authorship_order(self):
        """Test proper ordering of article authors."""
        a = Article.objects.get(slug='quantum-theory')
        yw = Collaborator.objects.get(email="yakko.warner@wbwatertower.com")
        a_aa = ArticleAuthorship(
                collaborator=yw, article=a, display_order=2,
                student_colleague=STUDENT_LEVELS['UNDERGRAD_STUDENT'])
        a_aa.save()
        authors = ['Einstein, Albert', 'Warner, Yakko']
        self.assertAuthorshipDisplayOrder(a, authors)

    def test_article_authorship_student_collaboration(self):
        """Test student colleague status for article authorship."""
        a = Article.objects.get(slug='quantum-theory')
        yw = Collaborator.objects.get(email="yakko.warner@wbwatertower.com")
        a_aa = ArticleAuthorship(
                collaborator=yw, article=a, display_order=2,
                student_colleague=STUDENT_LEVELS['UNDERGRAD_STUDENT'])
        a_aa.save()
        self.assertAuthorshipStudentStatus(
            a, ["yakko.warner@wbwatertower.com"], ["ae@example.edu"])



### Tests to add:
###   * test attaching a file 
###   * test getting primary file
###   * test relationship to grants
###   * test relationship to media mention
