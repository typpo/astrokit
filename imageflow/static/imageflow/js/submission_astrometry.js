function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function setupCsrfToken(csrftoken) {
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function setupListeners() {
  setupListener('set_datetime',
                $('#edit-image-datetime'),
                $('#edit-image-datetime-success'),
                $('#edit-image-datetime-failure'));

  setupListener('set_filter_band',
                $('#select-filter-name'),
                $('#select-filter-name-success'),
                $('#select-filter-name-failure'));

  setupListener('set_elevation',
                $('#set-elevation'),
                $('#set-elevation-success'),
                $('#set-elevation-failure'));

  setupListener('set_latitude',
                $('#set-latitude'),
                $('#set-latlng-success'),
                $('#set-latlng-failure'));

  setupListener('set_longitude',
                $('#set-longitude'),
                $('#set-latlng-success'),
                $('#set-latlng-failure'));
}

function setupListener(apiPath, $control, $success, $failure) {
  $control.on('change', function() {
    var val = $(this).val();

    document.body.style.cursor = 'wait';
    $.post('/submission/' + window.subid + '/' + apiPath, {val: val}, function(data) {
      $success.toggle(data.success);
      $failure.toggle(!data.success);
      document.body.style.cursor = 'default';
    });
  });
}

$(function() {
  setupCsrfToken(getCookie('csrftoken'));
  setupListeners();
});
