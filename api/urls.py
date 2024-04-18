from api import views, apps
from django.urls import path


app_name = apps.ApiConfig.name

urlpatterns = [
	path('',views.ContactAPIiew.as_view() , name='main'),
]
