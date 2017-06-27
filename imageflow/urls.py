from django.conf.urls import patterns, url

urlpatterns = patterns('imageflow.views',
    url(r'^upload', 'upload_image', name='upload_image'),
    url(r'^submission/(?P<subid>[0-9]+)$', 'astrometry', name='astrometry'),
    url(r'^submission/(?P<subid>[0-9]+)/set_datetime$', 'set_datetime', name='set_datetime'),
    url(r'^submission/(?P<subid>[0-9]+)/set_filter_band$', 'set_filter_band', name='set_filter_band'),
    url(r'^submission/astrometry/(?P<subid>[0-9]+)$', 'astrometry', name='astrometry'),
    url(r'^submission/point_sources/(?P<subid>[0-9]+)$', 'point_sources', name='point_sources'),
    url(r'^submission/reference_stars/(?P<subid>[0-9]+)$', 'reference_stars', name='reference_stars'),
    url(r'^submission/light_curve/(?P<subid>[0-9]+)$', 'light_curve', name='light_curve'),
    url(r'^api/submission/(?P<subid>[0-9]+)/results$', 'api_get_submission_results', name='api_get_submission_results'),
    url(r'^$', 'index', name='index'),
)
