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
  $('#edit-image-datetime').on('change', function() {
    var val = $(this).val();
    console.log('Datetime changed to', val);

    document.body.style.cursor = 'wait';
    $.post('/submission/' + window.subid + '/set_datetime', {
      image_datetime: val,
    }, function(data) {
      $('#edit-image-datetime-success').toggle(data.success);
      $('#edit-image-datetime-failure').toggle(!data.success);
      document.body.style.cursor = 'default';
    });
  });

  $('#select-filter-name').on('change', function() {
    var val = $(this).val();
    console.log('Select filter changed to', val);

    document.body.style.cursor = 'wait';
    $.post('/submission/' + window.subid + '/set_filter_band', {
      filter_band: val,
    }, function(data) {
      $('#select-filter-name-success').toggle(data.success);
      $('#select-filter-name-failure').toggle(!data.success);
      document.body.style.cursor = 'default';
    });
  });
}

$(function() {
  setupCsrfToken(getCookie('csrftoken'));
  setupListeners();
});
