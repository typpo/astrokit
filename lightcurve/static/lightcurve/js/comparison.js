(function() {
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
      // FIXME this doesn't work
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

  function setupComparisonStars() {
    $('.js-comparison-star-selection-table input').on('change', function() {
      var $tr = $(this).closest('tr');
      var selectedDesigs = $('.js-comparison-star-selection-table input:checked').map(function() {
        return $(this).data('star-desig');
      });

      $tr.addClass('warning');

      // Update backend.
      $.post('/lightcurve/' + window.lightcurveId + '/comparison_desigs', {
        desigs: JSON.stringify(selectedDesigs.toArray()),
      }, function(data) {
        $tr.removeClass('warning');
        if (!data.success) {
          alert('Sorry, something went wrong and we were not able to update your comparison star list.');
        } else {
          $tr.addClass('success');
          setTimeout(function() {
            $tr.removeClass('success');
          }, 800);
        }
      });
    });
  }

  $(function() {
    setupComparisonRefreshHandler();
    setupComparisonStars();
  });
})();
