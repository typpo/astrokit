function setupRunReductions() {
  $('.js-run-reductions').on('click', function() {
    $.post('/analysis/' + window.analysisId + '/set_reduction_status', {
      status: 'PENDING'
    }, function(data) {
      $('.reductions-loader').show();
      pollReductionStatus();
    });
    return false;
  });
}

function pollReductionStatus() {
  $.post('/analysis/' + window.analysisId + '/get_reduction_status', function(data) {
    if (data.status === 'COMPLETE') {
      $('.reductions-loader').hide();
      window.location.reload();
    } else {
      setTimeout(pollReductionStatus, 1000);
    }
  });
}

$(function() {
  setupListener('set_color_index_1',
                $('#select-color-index-1'),
                $('#select-color-index-success'),
                $('#select-color-index-failure'));

  setupListener('set_color_index_2',
                $('#select-color-index-2'),
                $('#select-color-index-success'),
                $('#select-color-index-failure'));

  setupListener('set_image_companion',
                $('input[name="image-companion"]'),
                $('#select-color-index-success'),
                $('#select-color-index-failure'));

  setupListener('set_second_order_extinction',
                $('#second-order-extinction'),
                $('#second-order-extinction-success'),
                $('#second-order-extinction-failure'));

  setupRunReductions();
});
