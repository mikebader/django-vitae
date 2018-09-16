from django.urls import path

from . import views

app_name = 'cv'
urlpatterns = [
    path('', views.cv_list, name='cv_list'),
    path('articles/', views.ArticleListView.as_view(), name='article_object_list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_object_detail'),
    path('articles/<slug:slug>/citation/<str:format>/', views.article_citation_view, name='article_citation'),

    path('books/', views.BookListView.as_view(), name='book_object_list'),
    path('books/<slug:slug>/', views.BookDetailView.as_view(), name='book_object_detail'),
    path('books/<slug:slug>/citation/<str:format>/', views.book_citation_view, name='book_citation'),

    path('reports/', views.ReportListView.as_view(), name='report_object_list'),
    path('reports/<slug:slug>/', views.ReportDetailView.as_view(), name='report_object_detail'),
    path('reports/<slug:slug>/citation/<str:format>/', views.report_citation_view, name='report_citation'),

    path('chapters/', views.ChapterListView.as_view(), name='chapter_object_list'),
    path('chapters/<slug:slug>/', views.ChapterDetailView.as_view(), name='chapter_object_detail'),
    path('chapters/<slug:slug>/citation/<str:format>/', views.chapter_citation_view, name='chapter_citation'),

    path('talks/', views.TalkListView.as_view(), name='talk_object_list'),
    path('talks/<slug:slug>/', views.TalkDetailView.as_view(), name='talk_object_detail'),
    path('talks/<slug:slug>/citation/<str:format>/', views.talk_citation_view, name='talk_citation'),

    # path('forms/article/add/', views.ArticleCreate.as_view(),name='article_new'),
    # path('forms/article/<int:pk>/edit/',views.ArticleUpdate.as_view(),name='article_edit'),

    path('<str:model_name>s/', views.CVListView.as_view(), name='section_list'),
    path('<str:model_name>s/<slug:slug>', views.CVDetailView.as_view(), name='item_detail'),
    # path('<str:model_name>s/<slug:slug>/<str:format>', name='citation'),

    path('forms/<str:model_name>/add/', views.CVCreateView.as_view(),name='cv_add'),
    path('forms/<str:model_name>/<int:pk>/edit/', views.CVUpdateView.as_view(),name='cv_edit'),
    path('forms/<str:model_name>/<int:pk>/delete/',views.CVDeleteView.as_view(), name='cv_delete'),
    ]