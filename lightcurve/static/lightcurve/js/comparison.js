function setupComparisonRefreshHandler() {
  $('.js-list-comparison').on('click', function() {
    $.post('/lightcurve/' + window.lightcurveId + '/status', {
      status: 'PHOTOMETRY_PENDING'
    }, function(data) {
      $('.page-loader').show();
      pollReductionStatus();
    });
    return false;
  });
}

function pollReductionStatus() {
  $.get('/lightcurve/' + window.lightcurveId + '/status', function(data) {
    if (data.status === 'REDUCTION_PENDING') {
      $('.page-loader').hide();
      alert('Photometry has completed. Press OK to refresh.');
      window.location.hash = 'select-comp-stars';
      window.location.reload();
    } else {
      setTimeout(pollReductionStatus, 1000);
    }
  });
}

$(function() {
  setupComparisonRefreshHandler();
});
