from django.urls import include, path

urlpatterns = [
	path('', include('cv.urls')),
]
