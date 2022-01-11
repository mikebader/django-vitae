from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template

from nose.plugins.attrib import attr

from tests.cvtests import VitaePublicationTestCase, AuthorshipTestCase

from cv.models import Article, ArticleAuthorship, Journal, Position, Chapter
from cv.settings import PUBLICATION_STATUS
from cv.utils import CSLCitation
from cv.templatetags.cv import CSLMalformedCitationWarning

import sys

@attr('template-tags')
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

        a4 = {
            'title': 'Forthcoming Article',
            'short_title': 'Forthcoming',
            'slug': 'forthcoming',
            'journal': j3,
            'status': PUBLICATION_STATUS['FORTHCOMING_STATUS']
        }

        a5 = {
            'title': 'Article in Preparation',
            'short_title': 'Inprep Article',
            'slug': 'inprep-article',
            'status': PUBLICATION_STATUS['INPREP_STATUS']
        }

        a6 = {
            'title': 'Article in Revision',
            'short_title': 'Revision Article',
            'slug': 'revise-article',
            'status': PUBLICATION_STATUS['REVISE_STATUS']
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
        cls.a4 = Article.objects.create(**a4)
        cls.a5 = Article.objects.create(**a5)
        cls.a6 = Article.objects.create(**a6)

        cls.authuser = User.objects.create_user(
            'testuser', 'test@example.com', 's3krit')

    def test_publication_entries(self):
        t = Template("""
            {% load cv %}
            {% publication_entries articles %}
        """)
        context = Context({
            'articles': Article.displayable.published(),
            'user': AnonymousUser()
        })
        rendered = t.render(context)
        html_test_text = (
            '<span class="cv-entry-citation cv-entry-citation-article">'
            'Einstein, A. On the Generalized '
            'Theory of Gravitation. '
            '<i>Scientific American</i>, <i>182</i>(4), 13–17.</span>'
        )

        self.assertInHTML(
            '1950&nbsp;',
            rendered)
        self.assertInHTML(html_test_text, rendered)

        # With authorized user
        context = Context({
            'articles': Article.displayable.published(),
            'user': self.authuser
        })
        rendered = t.render(context)
        html_test_text = '/forms/article/1/edit/'
        self.assertIn(html_test_text, rendered)

        # With forthcoming article
        context = Context({
            'articles': Article.objects.filter(slug__exact='forthcoming'),
            'user': AnonymousUser
        })
        rendered_template = t.render(context)
        test_text = "forth.&nbsp;"
        self.assertIn(test_text, rendered_template)

    def test_publication_list(self):
        t = Template("""
            {% load cv %}
            {% publication_list 'article' object_list %}
        """)
        context = Context({
            'object_list': {
                'published': Article.displayable.published(),
                'revise': Article.displayable.revise(),
                'inprep': Article.displayable.inprep()
            },
            'user': self.authuser
        })
        rendered = t.render(context)
        self.assertInHTML('<h3 class="cv-subsection cv-subsection-article cv-published cv-published-article">Published</h3>', rendered)
        self.assertInHTML('<h3 class="cv-subsection cv-subsection-article cv-revise cv-revise-article">Under Review</h3>', rendered)
        self.assertInHTML('<h3 class="cv-subsection cv-subsection-article cv-inprep cv-inprep-article">In Preparation</h3>', rendered)

    def test_section_list(self):
        t = Template("""
            {% load cv %}
            {% section_list 'article' object_list 'article heading' %}
        """)
        context = Context({
            'object_list': {
                'published': Article.displayable.published(),
                'revise': Article.displayable.revise(),
                'inprep': Article.displayable.inprep()
            },
            'user': self.authuser
        })
        rendered = t.render(context)
        a = Article.objects.get(slug='gen-theory-gravitation')
        self.assertInHTML(
            '<h2 id="article" class="cv-section-title">Article Heading</h2>',
            rendered
        )
        self.assertIn(CSLCitation(a).entry_parts()[1], rendered)

    def test_add_item(self):
        t = Template("""
            {% load cv %}
            {% add_item "article" %}
        """)

        # Authorized user
        context = Context({'user': self.authuser})
        rendered = t.render(context)
        html_test_text = '/forms/article/add/'
        self.assertIn(html_test_text, rendered)

        # Unauthorized user
        context = Context({'user': AnonymousUser()})
        rendered = t.render(context)
        self.assertEqual('', rendered.strip())

    def test_edit_item(self):
        t = Template("""
            {% load cv %}
            {% edit_item object %}
        """)

        # Authorized user
        context = Context({
            'object': Article.displayable.get(slug='gen-theory-gravitation'),
            'user': self.authuser
        })
        rendered = t.render(context)
        self.assertInHTML("""
            <a class="cv-edit cv-edit-article" href="/forms/article/1/edit/"
            title="Edit article">
            <i class="far fa-edit"></i></a>
        """, rendered)

        # Unauthorized user
        context = Context({
            'object': Article.displayable.get(slug='gen-theory-gravitation'),
            'user': AnonymousUser()
        })
        rendered = t.render(context)
        self.assertHTMLEqual('', rendered.strip())

    def test_print_collaborators(self):
        t = Template("""
            {% load cv %}
            {% print_collaborators article.authorship.all sep="; " two_sep=" & " last_sep="; & " %}
        """)

        # Single collaborator
        context = Context({
            'article': self.a
        })
        rendered = t.render(context)
        html_test_text = ('Albert Einstein')
        self.assertEqual(html_test_text, rendered.strip(),
                         'print_collaborators with one author '
                         'incorrectly formatted')

        # Two collaborators
        context = Context({
            'article': self.a2
        })
        rendered = t.render(context)
        html_test_text = ('Albert Einstein &amp; Jakob Laub')
        self.assertEqual(html_test_text, rendered.strip(),
                         'print_collaborators with two authors '
                         'incorrectly formatted')

        # Three collaborators
        context = Context({
            'article': self.a3
        })
        rendered = t.render(context)
        html_test_text = (
            'Albert Einstein; Richard C. Tolman; &amp; Boris Podolsky'
        )
        self.assertEqual(html_test_text, rendered.strip(),
                         'print_collaborators with three authors '
                         'incorrectly formatted')

        # Zero collaborators
        context = Context({
            'article': self.a4
        })
        rendered = t.render(context)
        self.assertEqual('', rendered.strip())

    def test_cite_item(self):
        t = Template("""
            {% load cv %}
            {% cite_item object %}
        """)
        context = Context({
            'object': Article.objects.get(slug='gen-theory-gravitation')
        })
        rendered = t.render(context)
        self.assertEqual(
            ('Einstein, A.  (1950). On the Generalized Theory of Gravitation. '
             '<i>Scientific American</i>, <i>182</i>(4), 13–17.'),
            rendered.strip()
        )

        # Incomplete citation
        chapter = Chapter.objects.create(**{
            'title': 'A Chapter with No Editor',
            'short_title': 'Chapter No Editor',
            'slug': 'chapter-no-editor',
            'book_title': 'A Book of Chapters',
            'status': PUBLICATION_STATUS['PUBLISHED_STATUS']
            })
        context = Context({'chapter': chapter})

        # Default behavior (warn)
        t = Template("""
            {% load cv %}
            {% cite_item chapter %}
        """)
        with self.assertWarns(CSLMalformedCitationWarning):
            rendered = t.render(context)
        self.assertEqual('', rendered.strip())

        # verbose
        t = Template("""
            {% load cv %}
            {% cite_item chapter 'verbose' %}
        """)
        with self.assertWarns(CSLMalformedCitationWarning) as w:
            rendered = t.render(context)
        self.assertIn('Citation not available.', rendered)

        # raise
        t = Template("""
            {% load cv %}
            {% cite_item chapter 'raise' %}
        """)
        with self.assertRaises(CSLCitation.CSLKeyError):
            t.render(context)


        # Bad cslerr parameter
        t = Template("""
            {% load cv %}
            {% cite_item chapter 'silent' %}
        """)
        with self.assertRaises(ValueError) as e:
            rendered = t.render(context)
        self.assertIn('Bad cslerr', str(e.exception))



    def test_cite_download(self):
        t = Template("""
            {% load cv %}
            {% cite_download object 'ris' %}
        """)
        context = Context({
            'object': Article.objects.get(slug='gen-theory-gravitation')
        })
        rendered = t.render(context)
        self.assertIn('/article/gen-theory-gravitation/cite/ris', rendered)

    def test_monetize(self):
        t = Template("""
            {% load cv %}
            {{1000|monetize:"£"}}
        """)
        rendered = t.render(Context({}))
        self.assertEqual('£1,000', rendered.strip())

    def test_year_range(self):
        position = Position.objects.create(**{
            'title': 'Professor',
            'institution': 'Institution',
            'start_date': '2000-01-01'
        })
        t = Template("""
            {% load cv %}
            {{position|year_range}}
        """)

        # Start date only
        context = Context({'position': position})
        rendered = t.render(context)
        self.assertEqual("2000–", rendered.strip())

        # Start date and end date in same year
        position.end_date = "2000-12-31"
        position.save()
        context = Context({'position': position})
        rendered = t.render(context)
        self.assertEqual("2000", rendered.strip())

        # Start date and end date different years
        position.end_date = "2001-12-31"
        position.save()
        context = Context({'position': position})
        rendered = t.render(context)
        self.assertEqual("2000–2001", rendered.strip())
