var compareIds = new Set();

function updateStar(starId, checked) {
  $('.js-reference-table')
      .find('tr[data-star-id="' + starId + '"]').toggleClass('success', checked)
      .find('input').attr('checked', checked)

  if (checked) {
    compareIds.add(starId);
  } else {
    compareIds.delete(starId);
  }
  $('#num-comparison-stars').text(compareIds.size);
}

function setupComparisonStarSelection() {
  $('td input').on('change', function() {
    var $this = $(this);
    var checked = $this.is(':checked');
    var $tr = $this.parent().parent();
    var starId = parseInt($tr.data('star-id'), 10);
    updateStar(starId, checked);

    // Update backend.
    $.post('/analysis/' + window.analysisId + '/comparison_stars', {
      ids: Array.from(compareIds),
    }, function(data) {
      if (!data.success) {
        alert('Sorry, something went wrong and we were not able to save your updated comparison star list.');
      }
    });
  });

}

function selectComparisonStars() {
  $.get('/analysis/' + window.analysisId + '/comparison_stars', function(data) {
    if (data.success) {
      data.ids.forEach(function(starId) { updateStar(starId, true) });
    }
  });
}

$(function() {
  setupMagnitudeChecks($('.plot-container'),
                       'instrumental',
                       window.catalogData,
                       window.catalogData);

  setupComparisonStarSelection();
  selectComparisonStars();

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
