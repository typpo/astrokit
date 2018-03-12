window.lightcurveStatus = {};

(function() {

var prevNumProcessed = -1;
function checkStatus() {
  $.get('/lightcurve/' + window.lightcurveId + '/status', function(data) {
    window.lightcurveStatus = data;
    $('.js-num-images-processed').text(data.numProcessed);
    $('.js-num-images-photometry').text(data.numPhotometry);
    $('.js-num-comparison-stars').text(data.numComparisonStars);
    $('.js-num-images-pair').text(data.numPairs);
    $('.js-num-images-target').text(data.numTarget);
    $('.js-num-images-reviewed').text(data.numReviewed);
    $('.js-num-images-reduction-complete').text(data.numReductionComplete);
    $('.js-num-images-lightcurve').text(data.numLightcurve);
    if (data.numImages === data.numProcessed &&
        data.numProcessed !== prevNumProcessed &&
        prevNumProcessed !== -1) {
      $('.js-new-results').show();
    }
    setTimeout(checkStatus, 5000);
    prevNumProcessed = data.numProcessed;
  });
}

function saveObservationDefault() {
  $.post('/lightcurve/' + window.lightcurveId + '/save_observation_default', {
    'lat': $('#set-latitude').val(),
    'lng': $('#set-longitude').val(),
    'elevation': $('#set-elevation').val(),
    'extinction': $('#second-order-extinction').val(),
    'target': $('#target-name').val(),
    'magband': $('#select-magband').val(),
  }, function(data) {
    if (data.success) {
      alert('Settings applied to all images.');
    } else {
      alert('Something went wrong. Settings were not applied to all images.');
    }
  });
}

function toggleAddToLightcurve(toggleButton) {
  $.post('/lightcurve/' + window.lightcurveId + '/add_image_toggle', {
    analysisId: $(toggleButton).data('analysis-id')
  }, function(data) {
    if (data.success) {
      $(toggleButton).toggleClass('btn-success');
      $(toggleButton).toggleClass('btn-default');
      if (data.added) {
        $(toggleButton).text('Remove from lightcurve');
      } else {
        $(toggleButton).text('Add to lightcurve');
      }
    } else {
      alert('Something went wrong. Changes were not applied to this image.');
    }
  });
}

function setupAddAllImages() {
  $('.js-add-images-lightcurve').on('click', function() {
    $('.page-loader').show();
    $('.js-add-images-lightcurve').attr('disabled', 1);
    addAllImages();
  });
}

function addAllImages() {
  $.post('/lightcurve/' + window.lightcurveId + '/add_images', {}, function(data) {
    if (data.success) {
      $('.page-loader').hide();
      $('.js-add-images-lightcurve').removeAttr('disabled');
      alert(data.count + ' images added to your light curve. Press OK to refresh.');
      window.location.hash = 'image-reductions';
      window.location.reload();
    } else {
      alert('Sorry, something went wrong and images could not be added to your lightcurve.');
    }
  });
}

function editLightCurveName(lightcurveId) {
  $.post('/lightcurve/' + lightcurveId + '/edit_lightcurve_name',
         $('.js-edit-name-form').serialize())
  .done(function() {
    window.location.reload();
  })
  .fail(function() {
    alert('Something went wrong. Lightcurve name was not updated.');
  })
}

function setupEditNameHandlers() {
  $('.js-edit-name-form').on('submit', function() {
    var lightcurve_id = $(this).data('lightcurve-id');
    editLightCurveName(lightcurve_id);
    return false;
  });

  $('.js-edit-name').on('click', function() {
    $('span.lightcurve-name').hide();
    $('input.lightcurve-name').css('display', 'inline-block');
    $(this).hide();
    $('.js-submit-name, .js-cancel').css('display', 'inline-block');
    return false;
  });

  $('.js-cancel').on('click', function() {
    var name = $('span.lightcurve-name').text();
    $('input.lightcurve-name').val(name);
    $('input.lightcurve-name').hide();
    $('span.lightcurve-name').css('display', 'inline-block');
    $('.js-edit-name').css('display', 'inline-block');
    $('.js-submit-name, .js-cancel').hide();
    return false;
  });
}

function setupMiscHandlers() {
  $('#save-observation-default').on('click', function() {
    saveObservationDefault();
    return false;
  });

  $('.js-toggle-lightcurve').on('click', function() {
    toggleAddToLightcurve(this);
    return false;
  });

  $('.js-reload').on('click', function() {
    window.location.reload();
    return false;
  });

  $('.select-target-link').on('click', function() {
    var analysisId = $(this).data('analysis-id');
    $('.iframe-target').attr('src', '/analysis/select_target_modal/' + analysisId);
  });
}

function setupImagePairs() {
  // Handle color index selection.
  var colorIndex = null;
  $('.js-select-color-index').on('change', function() {
    var val = $(this).val();
    if (val === 'NONE') {
      $('.image-pair-selector .btn').attr('disabled', 1);
    } else {
      $('.image-pair-selector .btn').removeAttr('disabled');
    }
    colorIndex = val;
  });

  // Handle pair selection.
  var $selectingElt = null;
  $('.js-select-image').on('click', function() {
    $selectingElt = $(this);
    $('input[name="image-radio"]').prop('checked', false);
    $('.select-image-modal .modal').modal();
  });

  $('.js-select-image-update').on('click', function() {
    var analysisId = $('input[name="image-radio"]:checked').val();
    if ($selectingElt) {
      if (analysisId && analysisId !== 'NONE') {
        $selectingElt.text('Image #' + analysisId);
        $selectingElt.data('analysis-id', analysisId);
        $selectingElt.removeClass('btn-primary').addClass('btn-default')
      } else {
        $selectingElt.text('Select Image');
        $selectingElt.addClass('btn-primary').removeClass('btn-default')
      }
    }
  });

  // Save everything.
  $('.js-save-image-pairs').on('click', function() {
    var data = {
      ciband: colorIndex,
      pairsJson: null,
    };

    var pairs = [];
    $('.js-select-image').each(function(idx) {
      var analysisId = parseInt($(this).data('analysis-id'), 0);
      if (isNaN(analysisId)) {
        analysisId = null;
      }

      // Build an array of pair tuples. eg.
      // [[1,2], [3,4], [5,6]]
      if (idx % 2 === 0) {
        pairs.push([analysisId]);
      } else {
        pairs[pairs.length - 1].push(analysisId);
      }
    });

    data.pairs = JSON.stringify(pairs);

    // TODO(ian): POST it all to some endpoint.
    $.post('/lightcurve/' + window.lightcurveId + '/save_image_pairs', data, function(result) {
      if (result.success) {
        alert('Your settings have been saved.');
      } else {
        alert('Sorry, something went wrong and your settings were not saved.');
      }
    });
  });
}

function setupModals() {
  $('.js-select-target').on('click', function() {
    var analysisId = $(this).data('analysis-id');
    $('.iframe-modal iframe').attr('src', '/analysis/select_target_modal/' + analysisId);
    $('.iframe-modal .modal').modal();
  });
}

$(function() {
  checkStatus();

  setupEditNameHandlers();
  setupMiscHandlers();
  setupImagePairs();
  setupModals();
  setupAddAllImages();
});

})();
