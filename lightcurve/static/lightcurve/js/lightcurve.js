var firstCheck = true;
function checkStatus() {
  $.get('/lightcurve/' + window.lightcurve_id + '/status', function(data) {
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
  $.post('/lightcurve/' + window.lightcurve_id + '/save_observation_default',
      {'lat': $('#set-latitude').val(),
       'lng': $('#set-longitude').val(),
       'elevation': $('#set-elevation').val(),
       'extinction': $('#second-order-extinction').val()},
      function(data) {
  });
}

$(function() {
  checkStatus();

  $('#save-observation-default').on('click', function() {
    saveObservationDefault();
  });

  $('.js-reload').on('click', function() {
    window.location.reload();
    return false;
  });
});
