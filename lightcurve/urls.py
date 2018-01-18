from django.conf.urls import patterns, url

urlpatterns = patterns('lightcurve.views',
    url(r'^edit/(?P<lightcurve_id>[0-9]+)$', 'edit_lightcurve', name='edit_lightcurve'),
)
