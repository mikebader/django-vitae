from django.urls import path

from . import views

app_name = 'cv'
urlpatterns = [
    path('', views.CVView.as_view(), name='cv_list'),
    path('pdf/', views.cv_pdf, name='cv_pdf'),

    path('forms/<str:model_name>/add/', views.CVCreateView.as_view(),name='cv_add'),
    path('forms/<str:model_name>/<int:pk>/edit/', views.CVUpdateView.as_view(),name='cv_edit'),
    path('forms/<str:model_name>/<int:pk>/delete/',views.CVDeleteView.as_view(), name='cv_delete'),

    path('<str:model_name>s/', views.CVListView.as_view(), name='section_list'),
    path('<str:model_name>s/<slug:slug>/', views.CVDetailView.as_view(), name='item_detail'),
    path('<str:model_name>s/<slug:slug>/cite/<str:format>/', views.citation_view, name='citation'),
    ]