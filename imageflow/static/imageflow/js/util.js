// TODO(ian): Move this file to a generic location.

function setupListener(apiPath, $control, $success, $failure, postVals) {
  postVals = postVals || {};
  $control.on('change', function() {
    var val = $(this).val();
    $success.toggle(false);
    $failure.toggle(false);

    document.body.style.cursor = 'wait';
    var postObj = Object.assign({val: val}, postVals);
    $.post('/analysis/' + window.analysisId + '/' + apiPath, postObj, function(data) {
      $success.toggle(data.success);
      $failure.toggle(!data.success);
      document.body.style.cursor = 'default';
    });
  });
}

