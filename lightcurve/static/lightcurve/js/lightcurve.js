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
  form_name = "#lightcurve_" + lightcurveId + "_title"
  $.post('/lightcurve/' + lightcurveId + '/save_lightcurve_changes', $(form_name).serialize()
  , function(data) {
    if (data.success) {
      alert('Settings applied to lightcurve.');
      window.location.reload();
    } else {
      alert('Something went wrong. Settings were not applied to lightcurve.');
    }
  });
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

  $(document).on('click', '.edit-name', function(e) {
    e.preventDefault();
    var filename = $(this).prev(".lightcurve-name").text();
    $( $(this).prev(".lightcurve-name") ).replaceWith( "<input type='name' class='input_name' name='input_name' value='" + filename + "'>" );
    $(this).replaceWith("<button type='submit' class='btn btn-sm btn-primary submit-name'>Save</button><button class='btn btn-sm btn-default cancel'>Cancel</button>");
  });

  $(document).on('click', '.cancel', function() {
    var filename = $(this).parent().find('.input_name').val();
    $( $(this).parent().find('.input_name') ).replaceWith( "<span class='lightcurve-name'>" + filename + "</span>" );
    $( $(this).prev('.submit-name') ).replaceWith("<button class='btn btn-xs btn-default edit-name'>Edit Name</button>");
    $(this).remove();
  });

});
