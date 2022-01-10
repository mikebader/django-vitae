from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import TestCase, Client, RequestFactory
from django.urls import resolve

from nose.plugins.attrib import attr

from cv.models import Article, ArticleAuthorship, Journal, Book, Position
from cv.settings import PUBLICATION_STATUS
from cv.utils import CSLCitation

from cv.views import CVListMixin, CVView, CVListView, CVDetailView,\
                     citation_view


@attr('views')
class ViewTestCase(TestCase):
    fixtures = ['cv/fixtures/fixture.json']

    c = Client()

    def setUp(self):
        self.factory = RequestFactory()
        self.article = Article.displayable.published()[0]

    def setup_view(self, view, request, *args, **kwargs):
        view.request = request
        view.args = args
        view.kwargs = resolve(request.path).kwargs
        return view

    # CV LIST MIXIN
    def test_cvlistmixin_get_cv_list(self):
        mixin = CVListMixin()

        # Class with single manager
        position_list = mixin.get_cv_list(Position)
        test_list = {
            'position_list': Position.displayable.all()
        }
        self.assertSetEqual(
            set(position_list['position_list']),
            set(test_list['position_list'])
        )

        # Class with multiple managers
        article_list = mixin.get_cv_list(Article)
        test_list = {'article_list': {
            'published': Article.displayable.published(),
            'revise': Article.displayable.revise(),
            'inprep': Article.displayable.inprep(),
            'total': 6
        }}
        self.assertEqual(list(article_list.keys()), ['article_list'])
        for k in ['published', 'revise', 'inprep']:
            self.assertSetEqual(
                set(article_list['article_list'][k]),
                set(test_list['article_list'][k])
            )
        self.assertEqual(article_list['article_list']['total'],
                         test_list['article_list']['total'])

    def test_cvlistmixin_get_cv_primary_positions(self):
        mixin = CVListMixin()

        self.assertSetEqual(
            set(mixin._get_cv_primary_positions()['primary_positions']),
            set(Position.primary_positions.all())
        )

    # CV VIEW
    def test_cvview_get_context_data(self):
        view = CVView()

        model_names = [
            'award', 'position', 'degree', 'article', 'book', 'chapter',
            'report', 'grant', 'talk', 'otherwriting', 'dataset',
            'service', 'journalservice', 'student', 'course'
        ]

        context_keys = ['{}_list'.format(n) for n in model_names]
        for k in context_keys:
            self.assertIn(k, view.get_context_data())

    # CV LIST VIEW
    def test_cvlistview_setup(self):
        request = self.factory.get('/articles/')
        view = self.setup_view(CVListView(), request)
        view.setup(view, **view.kwargs)
        self.assertEqual(getattr(view, 'model_name'), 'article')
        self.assertEqual(getattr(view, 'model'), Article)

    def test_cvlistview_get_context_data(self):
        context = self.client.get('/articles/').context
        self.assertEqual(context['model_name'], 'article')
        self.assertEqual(context['model_name_plural'], 'articles')
        self.assertEqual(context['section_template'], 'cv/sections/article.html')

    def test_cvlistview_get_queryset(self):
        context = self.client.get('/articles/').context
        ol = context['object_list']
        for k in ['published', 'revise', 'inprep', 'total']:
            self.assertIn(k, ol.keys())
        self.assertEqual(len(list(ol.keys())), 4)

    def test_cvlistview_get_template_names(self):
        self.assertTemplateUsed(
            self.client.get('/articles/'),
            'cv/lists/cv_list.html'
        )

    # CV DETAIL VIEW
    def test_cvdetailview_response(self):
        # Model not named in detail views available
        response = self.client.get('/positions/position-slug')
        self.assertEqual(response.status_code, 404)

        # Model named in detail views available
        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_cvdetailview_setup(self):
        # Model not named in detail views available
        request = self.factory.get('/positions/')
        view = self.setup_view(CVDetailView(), request)
        with self.assertRaises(Http404):
            view.setup(view, **view.kwargs)

        # Model named in detail views available
        request = self.factory.get(self.article.get_absolute_url())
        view = self.setup_view(CVDetailView(), request)
        view.setup(view, **view.kwargs)
        self.assertEqual(getattr(view, 'model_name'), 'article')
        self.assertEqual(getattr(view, 'model'), Article)

    def test_cvdetailview_get_context_data(self):
        aurl = self.article.get_absolute_url()
        context = self.client.get(aurl).context
        self.assertEqual(context['model_name'], 'article')
        self.assertEqual(context['model_name_plural'], 'articles')

    def test_cvdetailview_get_template_names(self):
        self.assertTemplateUsed(
            self.client.get(self.article.get_absolute_url()),
            'cv/details/cv_detail.html'
        )
        book = Book.displayable.published()[0]
        self.assertTemplateUsed(
            self.client.get(book.get_absolute_url()),
            'cv/details/book.html'
        )

    # CV CITATION VIEW
    def test_citation_view(self):
        a = Article.displayable.published()[0]
        aurl = a.get_absolute_url()

        # Valid format (ris)
        url = '{}cite/ris/'.format(aurl)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cv/citations/article.ris')
        self.assertEqual(
            response['content-type'], 'application/x-research-info-systems'
        )

        # Valid format (bib)
        url = '{}cite/bib/'.format(aurl)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cv/citations/article.bib')
        self.assertEqual(response['content-type'], 'application/x-bibtex')

        # Invalid format
        url = '{}cite/json/'.format(aurl)
        response = self.c.get(url)
        self.assertEqual(
            response.status_code, 404,
            'Invalid citation format did not return 404 status'
        )

        # Invalid model
        url = '/otherwriting/slug/cite/ris'
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, 404,
            '''Model type in not in DETAIL_VIEWS_AVAILABLE did not return
            404 status'''
        )
        with self.assertRaises(Http404):
            citation_view(request, 'otherwriting', 'slug', 'ris')

