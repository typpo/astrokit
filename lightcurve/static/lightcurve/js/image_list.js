function sortImages(option) {
  $.get('/lightcurve/' + window.lightcurveId + '/images',
         {'sort': $(option).val()} )
  .done(function(data) {
    $('#image-list').replaceWith($(data).find('#image-list'));
  })
  .fail(function() {
    alert('Something went wrong. Image list was not updated.');
  })
}

$(function() {
  $('#select-sort-images').on('change', function() {
    if ($(this).val()) {
      sortImages(this);
    }
    return false;
  });
});
