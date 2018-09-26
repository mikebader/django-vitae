from django.urls import path

from . import views

app_name = 'cv'
urlpatterns = [
    path('', views.cv_list, name='cv_list'),

    path('<str:model_name>s/', views.CVListView.as_view(), name='section_list'),
    path('<str:model_name>s/<slug:slug>', views.CVDetailView.as_view(), name='item_detail'),
    path('<str:model_name>s/<slug:slug>/<str:format>', views.citation_view, name='citation'),

    path('forms/<str:model_name>/add/', views.CVCreateView.as_view(),name='cv_add'),
    path('forms/<str:model_name>/<int:pk>/edit/', views.CVUpdateView.as_view(),name='cv_edit'),
    path('forms/<str:model_name>/<int:pk>/delete/',views.CVDeleteView.as_view(), name='cv_delete'),
    ]