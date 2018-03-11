
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

  setupListener('set_target_point_source',
                $('#target-id'),
                $('#target-id-success'),
                $('#target-id-failure'));

  $('#target-id').on('change', function() {
    window.targetId = parseInt($(this).val(), 10);
    setupPlot();
  });
  setupPlot();
}

$(function() {
  setupListeners();
});
