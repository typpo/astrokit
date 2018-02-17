$(function() {
  setupMagnitudeChecks($('.plot-container'),
                       'instrumental',
                       window.catalogData,
                       window.catalogData);

  $('td input').on('change', function() {
    var $this = $(this);
    var checked = $this.is(':checked');
    var $tr = $this.parent().parent();
    //$tr.toggleClass('success', checked);
    var starId = $tr.data('star-id');
    $('.js-reference-table')
        .find('tr[data-star-id="' + starId + '"]').toggleClass('success', checked)
        .find('input').attr('checked', true)
  });

  // Link both reference star lists together.
  var scrollTimer = null;
  $('.table-wrapper').on('scroll', function() {
    var me = this;
    var $this = $(this);
    clearTimeout(scrollTimer);
    setTimeout(function() {
      $('.table-wrapper').not(me).scrollTop($this.scrollTop());
    }, 100);
    return false;
  });
});
