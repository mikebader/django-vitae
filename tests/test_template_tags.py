from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template

from nose.plugins.attrib import attr

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase

from cv.models import Article, ArticleAuthorship, Journal
from cv.settings import PUBLICATION_STATUS

@attr('cvtags')
class TemplateTagTestCase(VitaePublicationTestCase, AuthorshipTestCase):

    @classmethod
    def setUp(cls):
        super(TemplateTagTestCase, cls).setUp()

        j = Journal.objects.create(title='Scientific American')

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

        a = Article.objects.create(**a)
        auth = ArticleAuthorship(
            collaborator=cls.einstein, article=a, display_order=1)
        auth.save()
        cls.a = a

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



