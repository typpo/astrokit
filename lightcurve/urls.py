from django.conf.urls import patterns, url

urlpatterns = patterns('lightcurve.views',
    url(r'^(?P<lightcurve_id>[0-9]+)/edit$', 'edit_lightcurve', name='edit_lightcurve'),
    url(r'^(?P<lightcurve_id>[0-9]+)/plot$', 'plot_lightcurve', name='plot_lightcurve'),
    url(r'^(?P<lightcurve_id>[0-9]+)/plot_json$', 'plot_lightcurve_json', name='plot_lightcurve_json'),
    url(r'^(?P<lightcurve_id>[0-9]+)/status$', 'status', name='status'),
    url(r'^(?P<lightcurve_id>[0-9]+)/save_observation_default$', 'save_observation_default', name='save_observation_default'),
    url(r'^(?P<lightcurve_id>[0-9]+)/apply_photometry_settings$', 'apply_photometry_settings', name='apply_photometry_settings'),
    url(r'^(?P<lightcurve_id>[0-9]+)/save_image_pairs$', 'save_image_pairs', name='save_image_pairs'),
    url(r'^(?P<lightcurve_id>[0-9]+)/add_images$', 'add_images', name='add_images'),
    url(r'^(?P<lightcurve_id>[0-9]+)/add_image_toggle$', 'add_image_toggle', name='add_image_toggle'),
    url(r'^(?P<lightcurve_id>[0-9]+)/comparison_desigs$', 'comparison_desigs', name='comparison_desigs'),
    url(r'^(?P<lightcurve_id>[0-9]+)/edit_lightcurve_name$', 'edit_lightcurve_name', name='edit_lightcurve_name'),
    url(r'^(?P<lightcurve_id>[0-9]+)/download$', 'download', name='download'),
    url(r'^(?P<lightcurve_id>[0-9]+)/run_image_reductions$', 'run_image_reductions', name='run_image_reductions'),
    url(r'^my-lightcurve$', 'my_lightcurve', name='my_lightcurve'),
    url(r'^all-lightcurve$', 'all_lightcurve', name='all_lightcurve'),
)
