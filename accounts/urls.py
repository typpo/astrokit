from django.conf.urls import patterns, url
from .views import (
	LoginView,
	LogoutView,
	RegistrationView)

urlpatterns = patterns('imageflow.views',
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^register/', RegistrationView.as_view(), name='register'),
)
