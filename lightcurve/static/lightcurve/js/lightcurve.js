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
$(function() {
  checkStatus();

  $('.js-reload').on('click', function() {
    window.location.reload();
    return false;
  });
});
