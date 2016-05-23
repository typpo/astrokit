from django.conf.urls import patterns, url

urlpatterns = patterns('imageflow.views',
    url(r'^upload', 'upload_image', name='upload_image'),
    url(r'^api/submission/results', 'api_get_submission_results', name='api_get_submission_results'),
    url(r'^', 'index', name='index'),
)
