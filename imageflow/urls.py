from django.conf.urls import patterns, url

urlpatterns = patterns('imageflow.views',
    url(r'^upload', 'upload_image', name='upload_image'),
)
