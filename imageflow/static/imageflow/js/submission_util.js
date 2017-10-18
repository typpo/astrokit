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
