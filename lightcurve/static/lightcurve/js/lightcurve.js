$(function() {
  $('.js-run-astrometry').on('click', function() {
    var me = $(this);
    if (me.attr('disabled')) {
      return false;
    }
    me.attr('disabled', 1);
    me.text('Running astrometry...');

    var imageId = me.data('image-id');
    $.post('/lightcurve/submit_astrometry/' + imageId, function(data) {
      console.log('submit_astrometry response:', data);
    });
    return false;
  });
});
