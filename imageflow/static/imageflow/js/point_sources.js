function setupListeners() {
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
}

function setupRunPhotometry() {
  $('.js-run-photometry').on('click', function() {
    $.post('/analysis/' + window.analysisId + '/status', {
      status: 'PHOTOMETRY_PENDING',
    }, function(data) {
      if (!data.success) {
        alert('Sorry, something went wrong and your photometry job could not be started.');
        return;
      }
      $('.page-loader').show();
      setTimeout(pollPhotometryStatus, 2000);
    });
    return false;
  });
}

function pollPhotometryStatus() {
  $.get('/analysis/' + window.analysisId + '/status', function(data) {
    if (!data.success) {
      $('.page-loader').hide();
      alert('Sorry, something went wrong and your photometry run was not successful.');
    } else if (data.status !== 'PHOTOMETRY_PENDING') {
      $('.page-loader').hide();
      alert('Done! Press OK to reload the page.')
      window.location.reload();
    } else {
      setTimeout(pollPhotometryStatus, 1000);
    }
  });
}

$(function() {
  setupListeners();
  setupRunPhotometry();
});
