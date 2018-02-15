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

  setupListener('photometry_params',
                $('#photometry-iters'),
                $('#photometry-param-success'),
                $('#photometry-param-failure'),
                {param: 'iters'});

  setupListener('set_target_point_source',
                $('#target-id'),
                $('#target-id-success'),
                $('#target-id-failure'));

  $('#target-id').on('change', function() {
    window.targetId = $(this).val();
  });
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
    return false;
  });
}

$(function() {
  setupListeners();
  setupRunPhotometry();
  setupBlinking();
});
