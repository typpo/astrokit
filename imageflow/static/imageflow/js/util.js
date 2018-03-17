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

function setupTables() {
  var $tableWrapper = $('.table-wrapper').on('scroll', function() {
    $(this).find('thead').css('transform', 'translate(0,' + this.scrollTop + 'px)');
  });
  if ($().stupidtable) {
    $tableWrapper.find('table').stupidtable();
  }
  $('.js-scroll-to-target').on('click', function() {
    scrollToTarget($(this).parent().prev());
    return false;
  });
}

function scrollToTarget($wrapper) {
  var $elt = $wrapper.find('tr.highlight');
  $wrapper.animate({
    scrollTop: $wrapper.scrollTop() + ($elt.position().top - $wrapper.position().top) - ($wrapper.height()/2) + ($elt.height()/2),
  });
}


function setupTooltips() {
  // Initialize tooltips.
  if ($().tooltip) {
    $('[data-toggle="tooltip"]').tooltip({container: 'body'})
  }
}

$(function() {
  setupTables();
  setupTooltips();
});
