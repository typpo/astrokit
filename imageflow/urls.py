from django.conf.urls import patterns, url

from .views import ImageUploadView

urlpatterns = patterns('',
    url(r'^upload', ImageUploadView.as_view(), name='form'),
)
