$(function() {
  window.addEventListener('plot complete', function() {
    var $frame = $('.iframe-target', window.parent.document);
    var height = $('body').height() + 100;
    $frame.height(height);
  });
});
