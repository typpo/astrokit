$(function() {
  setupListener('photometry_params',
                $('#photometry-sigma'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'sigma'});

  setupListener('photometry_params',
                $('#photometry-threshold'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'threshold'});

  setupListener('photometry_params',
                $('#photometry-separation'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'separation'});

  setupListener('photometry_params',
                $('#photometry-fitshape'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'fitshape'});
});
