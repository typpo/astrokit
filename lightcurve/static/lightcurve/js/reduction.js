(function() {
  function setupRunReductions() {
    $('.js-run-lightcurve-reductions').on('click', function() {
      $.post('/lightcurve/' + window.lightcurveId + '/status', {
        status: 'REDUCTION_PENDING'
      }, function(data) {
        $('.page-loader').show();
        pollReductionStatus();
      });
      return false;
    });
  }

  function pollReductionStatus() {
    $.get('/lightcurve/' + window.lightcurveId + '/status', function(data) {
      if (data.status === 'REDUCTION_COMPLETE') {
        $('.page-loader').hide();
        alert('Your reduction has completed. Press OK to refresh.');
        window.location.hash = 'calculations';
        window.location.reload();
      } else {
        setTimeout(pollReductionStatus, 1000);
      }
    });
  }

  $(function() {
    setupRunReductions();
  });
})();
