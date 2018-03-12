$(function() {
  $('#target-id').on('change', function() {
    window.targetId = parseInt($(this).val(), 10);
    setupPlot();
  });

  window.addEventListener('plot complete', function() {
    var $frame = $('.iframe-target', window.parent.document);
    var height = $('body').height() + 20;
    $frame.height(height);
  });
});
