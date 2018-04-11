from django.conf.urls import patterns, url

urlpatterns = patterns('content.views',
    url(r'^science$', 'science', name='science'),
    url(r'^about$', 'about', name='about'),
)
