// TODO(ian): Move this file to a generic location.

function setupListener(apiPath, $control, $success, $failure) {
  $control.on('change', function() {
    var val = $(this).val();
    $success.toggle(false);
    $failure.toggle(false);

    document.body.style.cursor = 'wait';
    $.post('/submission/' + window.subid + '/' + apiPath, {val: val}, function(data) {
      $success.toggle(data.success);
      $failure.toggle(!data.success);
      document.body.style.cursor = 'default';
    });
  });
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

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
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

$(function() {
  setupCsrfToken(getCookie('csrftoken'));
});
