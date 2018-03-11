(function() {
  function setupRunReductions() {
    $('.js-run-lightcurve-reductions').on('click', function() {
      $.post('/lightcurve/' + window.lightcurveId + '/status', {
        status: 'REDUCTION_PENDING'
      }, function(data) {
        $('.js-run-image-reductions').attr('disabled', 1);
        $('.page-loader').show();
        pollLightcurveReductionStatus();
      });
      return false;
    });
  }

  function setupRunAllReductions() {
    $('.js-run-image-reductions').on('click', function() {
      $('.page-loader').show();

      $.post('/lightcurve/' + window.lightcurveId + '/run_image_reductions', {}, function(data) {
        pollImageReductionStatus();
      });
      return false;
    });
  }

  function pollLightcurveReductionStatus() {
    /*
    $.get('/lightcurve/' + window.lightcurveId + '/status', function(data) {
      if (data.status === 'REDUCTION_COMPLETE') {
      } else {
        setTimeout(pollReductionStatus, 1000);
      }
    });
   */
    if (window.lightcurveStatus.status === 'REDUCTION_COMPLETE') {
      $('.page-loader').hide();
      alert('Your reduction has completed. Press OK to refresh.');
      window.location.hash = 'calculations';
      window.location.reload();
    } else {
      setTimeout(pollLightcurveReductionStatus, 1000);
    }
  }


  function pollImageReductionStatus() {
    if (window.lightcurveStatus.numReviewed >= window.lightcurveStatus.numTarget) {
      $('.js-run-image-reductions').removeAttr('disabled');
      $('.page-loader').hide();
      alert('Images with targets have completed reduction. Press OK to refresh.');
      window.location.hash = 'review-analyses';
      window.location.reload();
    } else {
      setTimeout(pollImageReductionStatus, 1000);
    }
  }

  $(function() {
    setupRunReductions();
    setupRunAllReductions();
  });
})();
