function setupListeners() {
  setupListener('photometry_params',
                $('#photometry-aperture'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'aperture'});

  setupListener('photometry_params',
                $('#photometry-pixscale'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'pixscale'});

  setupListener('photometry_params',
                $('#photometry-gain'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'gain'});

  setupListener('photometry_params',
                $('#photometry-saturlevel'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'saturlevel'});

  setupListener('set_target_point_source',
                $('#target-id'),
                $('#target-id-success'),
                $('#target-id-failure'));

  $('#target-id').on('change', function() {
    window.targetId = parseInt($(this).val(), 10);
    setupPlot();
  });
}

function setupRunPhotometry() {
  $('.js-run-photometry').on('click', function() {
    $('.page-loader').show();
    $.post('/analysis/' + window.analysisId + '/status', {
      status: 'PHOTOMETRY_PENDING',
    }, function(data) {
      if (!data.success) {
        alert('Sorry, something went wrong and your photometry job could not be started.');
        return;
      }
      setTimeout(pollPhotometryStatus, 2000);
    });
    return false;
  });

  $('.js-apply-photometry').on('click', function() {
    if (!confirm('This will overwrite photometry settings and reset targets for all images in this lightcurve.\n\nAre you sure you want to do this?  Press cancel to exit.')) {
      return;
    }

    $('.page-loader').show();
    $('.js-apply-photometry').attr('disabled', 1);

    $.post('/lightcurve/' + window.lightcurveId + '/apply_photometry_settings', {
      analysisId: window.analysisId,
    }, function(data) {
      $('.page-loader').hide();
    $('.js-apply-photometry').removeAttr('disabled');

      if (data.success) {
        alert('Success! ' + data.numUpdated + ' images had their photometry parameters changed.');
      } else {
        alert('Sorry, something went wrong and your settings were not applied.');
      }
    });
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
      if (window.location.search.indexOf('select_target') > -1) {
        window.location.reload();
      } else {
        window.location.search += '&select_target=1';
      }
    } else {
      setTimeout(pollPhotometryStatus, 1000);
    }
  });
}


var blinkTimeout = null;
function doBlink($imgs, idx) {
  $imgs.hide();
  $($imgs[idx]).show();
  blinkTimeout = setTimeout(function() {
    doBlink($imgs, ++idx % $imgs.length);
  }, 600);
}

function setupBlinking() {
  $('.js-start-blinking').on('click', function() {
    $(this).hide();
    $('.js-stop-blinking').show();
    doBlink($('.js-blinkable'), 0);
    return false;
  });
  $('.js-stop-blinking').on('click', function() {
    clearTimeout(blinkTimeout);
    $(this).hide();
    $('.js-start-blinking').show();
    $('.js-blinkable').show();
    return false;
  });
}

$(function() {
  setupListeners();
  setupRunPhotometry();
  setupBlinking();
  setupPlot();
});
