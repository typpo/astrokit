
$(function() {
  setupListener('set_color_index_1',
                $('#select-color-index-1'),
                $('#select-color-index-success'),
                $('#select-color-index-failure'));

  setupListener('set_color_index_2',
                $('#select-color-index-2'),
                $('#select-color-index-success'),
                $('#select-color-index-failure'));

  setupListener('set_second_order_extinction',
                $('#second-order-extinction'),
                $('#second-order-extinction-success'),
                $('#second-order-extinction-failure'));
});
