var firstCheck = true;
function checkStatus() {
  $.get('/lightcurve/' + window.lightcurveId + '/status', function(data) {
    $('#num-images-processed').text(data.numProcessed);
    if (data.complete && !firstCheck) {
      $('.js-new-results').show();
    } else if (!data.complete) {
      setTimeout(checkStatus, 2000);
    }
    firstCheck = false;
  });
}

function saveObservationDefault() {
  $.post('/lightcurve/' + window.lightcurveId + '/save_observation_default', {
    'lat': $('#set-latitude').val(),
    'lng': $('#set-longitude').val(),
    'elevation': $('#set-elevation').val(),
    'extinction': $('#second-order-extinction').val()
  }, function(data) {
    if (data.success) {
      alert('Settings applied to all images.');
    } else {
      alert('Something went wrong. Settings were not applied to all images.');
    }
  });
}

function toggleAddToLightcurve(toggleButton) {
  $.post('/lightcurve/' + window.lightcurveId + '/add_image_toggle', {
    'analysis_id' : $(toggleButton).data('analysis-id')
  }, function(data) {
    if (data.success) {
      $(toggleButton).toggleClass('btn-success');
      $(toggleButton).toggleClass('btn-default');
      if (data.added) {
        $(toggleButton).text('Remove from lightcurve');
      } else {
        $(toggleButton).text('Add to lightcurve');
      }
    } else {
      alert('Something went wrong. Changes were not applied to this image.');
    }
  });
}

function saveLightcurveChanges(lightcurveId) {
  $.post('/lightcurve/' + lightcurveId + '/save_lightcurve_changes', $('form').serialize())
  .done(function() {
    alert('Settings applied to lightcurve.');
    window.location.reload();
  })
  .fail(function() {
    alert('Something went wrong. Settings were not applied to lightcurve.');
  })
}

$(function() {
  checkStatus();

  $('#save-observation-default').on('click', function() {
    saveObservationDefault();
    return false;
  });

  $('.js-toggle-lightcurve').on('click', function() {
    toggleAddToLightcurve(this);
    return false;
  });

  $('.js-reload').on('click', function() {
    window.location.reload();
    return false;
  });

  $('.js-edit-name-form').on('submit', function() {
    var lightcurve_id = $(this).data('lightcurve-id');
    saveLightcurveChanges(lightcurve_id);
    return false;
  });

  $('.js-edit-name').on('click', function() {
    $('span.lightcurve-name').hide();
    $('input.lightcurve-name').css('display', 'inline-block');
    $(this).hide();
    $('.js-submit-name, .js-cancel').css('display', 'inline-block');
    return false;
  });

  $('.js-cancel').on('click', function() {
    var name = $('span.lightcurve-name').text();
    $('input.lightcurve-name').val(name);
    $('input.lightcurve-name').hide();
    $('span.lightcurve-name').css('display', 'inline-block');
    $('.js-edit-name').css('display', 'inline-block');
    $('.js-submit-name, .js-cancel').hide();
    return false;
  });

});
