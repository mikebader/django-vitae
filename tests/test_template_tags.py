from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template

from nose.plugins.attrib import attr

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase

from cv.models import Article, ArticleAuthorship, Journal
from cv.settings import PUBLICATION_STATUS
import cv.templatetags as cvtags

@attr('cvtags')
class TemplateTagTestCase(VitaePublicationTestCase, AuthorshipTestCase):

    @classmethod
    def setUp(cls):
        super(TemplateTagTestCase, cls).setUp()

        j = Journal.objects.create(title='Scientific American')
        j2 = Journal.objects.create(title='Annalen der Physik')
        j3 = Journal.objects.create(title='Physical Review')

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

        a2 = {
            'title': 'On the Fundamental Electromagnetic Equations '
                     'for Moving Bodies',
            'short_title': 'Fundemental Electromagnetic Equations',
            'slug': 'fundamental-electromagnetic-equations',
            'journal': j2,
            'issue': 26, 'start_page': 532, 'end_page': 540,
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }

        a3 = {
            'title': 'Knowledge of past and future in quantum mechanics',
            'short_title': 'Past and Future in Quantum Mechanics',
            'slug': 'past-future-quantum-mechanics',
            'journal': j3,
            'issue': 37, 'start_page':780, 'end_page':781,
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
        }

        cls.a = Article.objects.create(**a)
        auth = ArticleAuthorship(
            collaborator=cls.einstein, article=cls.a, display_order=1)
        auth.save()

        cls.a2 = Article.objects.create(**a2)
        for i, x in enumerate([cls.einstein, cls.laub]):
            auth = ArticleAuthorship(
                collaborator=x, article=cls.a2,
                display_order=i)
            auth.save()

        cls.a3 = Article.objects.create(**a3)
        for i, x in enumerate([cls.einstein, cls.tolman, cls.podolsky]):
            auth = ArticleAuthorship(
                collaborator=x, article=cls.a3,
                display_order=i)
            auth.save()

    def test_publication_entries(self):
        """Test contents of publication_entries inclusion tag."""
        context = Context({
            'articles': Article.displayable.published(),
            'user': AnonymousUser()
        })
        template = Template(
            '{% load cvtags %}\n'
            '{% publication_entries articles %}')
        rendered_template = template.render(context)
        html_test_text = (
            '<span class="citation">Einstein, A. On the Generalized '
            'Theory of Gravitation. '
            '<i>Scientific American</i>, <i>182</i>(4), 13–17.</span>'
        )

        self.assertInHTML(
            '<span class="cv-entry-date col-2 col-sm-1">1950&nbsp;</span>',
            rendered_template)
        self.assertInHTML(html_test_text, rendered_template)

    def test_publication_entries_tag_authorized_user(self):
        user = User.objects.create_user(
            'testuser', 'test@example.com', 's3krit')
        template = Template(
            '{% load cvtags %}\n'
            '{% publication_entries articles %}')
        context = Context({
            'articles': Article.displayable.published(),
            'user': user
        })
        rendered_template = template.render(context)
        html_test_text = (
            '<a class="ml-4 article-edit cv-edit" '
            'href="/forms/article/1/edit/"><i class="far fa-edit"></i></a>'
        )
        self.assertInHTML(html_test_text, rendered_template)

    def test_publication_add_tag(self):
        user = User.objects.create_user(
            'testuser', 'test@example.com', 's3krit')
        template = Template(
            '{% load cvtags %}'
            '{% add_publication "article" %}'
        )
        context = Context({'user': user})
        rendered_template = template.render(context)
        html_test_text = (
            '<a class="article-add cv-add" alt="Add new article" '
            'href="/forms/article/add/"><i class="far fa-plus-square"></i>'
            ' Add new article</a>'
        )
        self.assertInHTML(html_test_text, rendered_template)

    def test_publication_add_not_authorized(self):
        user = AnonymousUser()
        template = Template(
            '{% load cvtags %}'
            '{% add_publication "article" %}'
        )
        context = Context({'user': user})
        rendered_template = template.render(context)
        self.assertHTMLEqual('', rendered_template)

    def test_print_authors_returns_formatted_text_one_author(self):
        """Tests print_authors filter provides author list with formats."""
        user = AnonymousUser()
        template = Template(
            '{% load cvtags %}'
            '{{article|print_authors}}'
        )
        context = Context({
            'article': self.a,
            'user': user
        })
        rendered_template = template.render(context)
        html_test_text = ('Albert Einstein')
        self.assertEqual(html_test_text, rendered_template,
                         'Default print_authors with two authors '
                         'incorrectly formatted')

    def test_print_authors_returns_formatted_text_two_authors(self):
        """Tests print_authors filter provides author list with formats."""
        user = AnonymousUser()
        template = Template(
            '{% load cvtags %}'
            '{{article|print_authors}}'
        )
        context = Context({
            'article': self.a2,
            'user': user
        })
        rendered_template = template.render(context)
        html_test_text = ('Albert Einstein and Jakob Laub')
        self.assertEqual(html_test_text, rendered_template,
                         'Default print_authors with two authors '
                         'incorrectly formatted')


    def test_print_authors_returns_formatted_text_three_authors(self):
        """Tests print_authors filter provides author list with formats."""
        user = AnonymousUser()
        template = Template(
            '{% load cvtags %}'
            '{{article|print_authors}}'
        )
        context = Context({
            'article': self.a3,
            'user': user
        })
        rendered_template = template.render(context)
        html_test_text = ('Albert Einstein, Richard C. Tolman, and Boris Podolsky')
        self.assertEqual(html_test_text, rendered_template,
                         'Default print_authors with three authors '
                         'incorrectly formatted')

