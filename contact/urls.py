from contact import views, apps
from django.urls import path


app_name = apps.ContactConfig.name

urlpatterns = [
	path('',views.ContactFormView.as_view() , name='main'),
]
