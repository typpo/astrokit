var IMAGE_TO_PLOT_XY_CONVERSION_FACTOR = 0;

function plotImage($container, canvas, imageUrl, opts) {
  // First, write the original image to canvas.
  var ctx = canvas.getContext('2d');
  var img = new Image();
  img.onload = function() {
    // Scale the width and height of plotted canvas images to a reasonable
    // size.  See issue #71
    var hRatio = opts.width / img.width;
    var vRatio = opts.height / img.height;
    var ratio = Math.min(hRatio, vRatio);
    IMAGE_TO_PLOT_XY_CONVERSION_FACTOR = ratio;

    canvas.width = Math.min(opts.width, img.width * ratio);
    canvas.height = Math.min(opts.height, img.height * ratio);
    $container.width(canvas.width);
    $container.height(canvas.height);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, img.width, img.height,
									0, 0, img.width * ratio, img.height * ratio);

    // Then plot stars from the data source.
    if (window.catalogData) {
      plotStars(canvas, window.catalogData, {
        color: 'red',
        radius: 9,
        text: function(star) {
          return star.designation;
        }
      });
    }
    if (window.pointSourceData) {
      plotStars(canvas, window.pointSourceData, {
        color: 'green',
        radius: 6,
        text: window.catalogData ?
          function(star) { return null; } : function(star) { return star.id },
      });
    }
  };
  img.src = imageUrl;
}

function plotStars(canvas, stars, rawOpts) {
  var opts = Object.assign({
    color: 'yellow',
    radius: 7,
    text: function(star) { return star.id },
  }, rawOpts);
  for (var i=0; i < stars.length; i++) {
    var star = stars[i];
    var starX = star.field_x * IMAGE_TO_PLOT_XY_CONVERSION_FACTOR;
    var starY = star.field_y * IMAGE_TO_PLOT_XY_CONVERSION_FACTOR;

    // Plot catalog stars over an image.
    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    // Circle - defined by x, y, radius, ...
    ctx.arc(starX, starY, opts.radius, 0, Math.PI * 2);
    ctx.strokeStyle = star.id === window.targetId ? 'cyan' : opts.color;
    ctx.lineWidth = 4;
    ctx.stroke();

    // Label
    var text = opts.text(star);
    if (!text) {
      continue;
    }

    ctx.font = '14px Arial';
    ctx.strokeStyle= 'black';
    ctx.lineWidth = 6;
    var labelWidth = ctx.measureText(text).width;
    ctx.strokeText(text, starX - (labelWidth / 2), starY - 8);
    ctx.fillStyle = 'yellow';
    ctx.fillText(text, starX - (labelWidth / 2), starY - 8);
  }
}

function getMousePos(canvas, evt) {
  var rect = canvas.getBoundingClientRect();
  return {
    x: evt.clientX - rect.left,
    y: evt.clientY - rect.top
  };
}

function setupCanvasListeners(canvas) {
  var xPosElt = document.getElementById('canvas-x-pos');
  var yPosElt = document.getElementById('canvas-y-pos');

  canvas.onmousemove = function onMouseover(e) {
    // Update mouse position display.
    var pos = getMousePos(canvas, e);
    xPosElt.innerHTML = parseInt(pos.x / IMAGE_TO_PLOT_XY_CONVERSION_FACTOR, 10);
    yPosElt.innerHTML = parseInt(pos.y / IMAGE_TO_PLOT_XY_CONVERSION_FACTOR, 10);
  }
}

function setupTables() {
  $('.table-wrapper').on('scroll', function() {
    $(this).find('thead').css('transform', 'translate(0,' + this.scrollTop + 'px)');
  });
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

function setupNotes() {
  $('.js-notes').on('change', function() {
    $.post('/analysis/' + window.analysisId + '/notes', { val: $(this).val() });
  });
}

function setupMagnitudeChecks($elts, type, xData, yData) {
  // Standard and instrumental mags vs catalog mags.
  $elts.each(function() {
    var $elt = $(this);
    var chart = [
      {
        x: xData.map(function(r) {
          return r[window.urat1Key];
        }),
        y: yData.map(function(r) {
          return type === 'instrumental' ? r.mag_instrumental : r.mag_standard;
        }),
        type: 'scatter',
        mode: 'markers',
      },
    ];
    var layout = {
      xaxis: {
        title: 'Standard Catalog Mag',
      },
      yaxis: {
        title: type === 'instrumental' ? 'Instrumental Mag' : 'Standard Mag (computed)',
      },
    };

    Plotly.newPlot($elt[0], chart, layout);
  });
}

$(function() {
  var canvas = document.getElementById('star-plot');
  if (canvas) {
    var $container = $('#plot-container');
    plotImage($container, canvas, window.originalImageUrl, {
      width: $container.width(),
      height: $container.height(),
    });
    setupCanvasListeners(canvas);
  }

  setupTables();
  setupNotes();

  // Initialize tooltips.
  if ($().tooltip) {
    $('[data-toggle="tooltip"]').tooltip({container: 'body'})
  }
});
