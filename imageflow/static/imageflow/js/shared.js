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

    // Determine color of circle.
    var myColor = opts.color;
    if (star.id === window.targetId) {
      myColor = 'cyan';
    } else if (typeof window.compareIds !== 'undefined' && compareIds.has(star.id)) {
      myColor = '#4B0082';
    }

    // Plot catalog stars over an image.
    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    // Circle - defined by x, y, radius, ...
    ctx.arc(starX, starY, opts.radius, 0, Math.PI * 2);
    ctx.strokeStyle = myColor;
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
    var offset = starY < 14 * 2 ? 14 + 8 : -8;
    ctx.strokeText(text, starX - (labelWidth / 2), starY + offset);
    ctx.fillStyle = 'yellow';
    ctx.fillText(text, starX - (labelWidth / 2), starY + offset);
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

function getLinearFit(xPoints, yPoints) {
  var zip = [];
  for (var i=0; i < xPoints.length; i++) {
    zip.push([xPoints[i], yPoints[i]]);
  }
  var result = regression.linear(zip);
  var slope = result.equation[0];
  var intercept = result.equation[1];
  return result.points;
}

function setupMagnitudeChecks($elts, type, xData, yData) {
  var xPoints = [];
  var yPoints = [];
  var colors = [];
  var texts = [];
  for (var i=0; i < xData.length; i++) {
    var xr = xData[i];
    var yr = yData[i];
    var yVal = type === 'instrumental' ? yr.mag_instrumental : yr.mag_standard;
    var xVal = xr[window.urat1Key];
    if (xVal && yVal) {
      xPoints.push(xVal);
      yPoints.push(yVal);
      colors.push(xr.is_comparison ? '#f00' : '#337ab7');
      texts.push('Object #' + xr.id + ': ' + xr.designation);
    }
  }
  var lineFit = getLinearFit(xPoints, yPoints);

  // Standard and instrumental mags vs catalog mags.
  $elts.each(function() {
    var $elt = $(this);
    var chart = [
      {
        name: 'Line of Fit',
        x: lineFit.map(function(p) { return p[0] }),
        y: lineFit.map(function(p) { return p[1] }),
        type: 'scatter',
        mode: 'lines',
        line: {
          color: '#aaa',
          width: 1,
        },
      },
      {
        name: 'Objects',
        x: xPoints,
        y: yPoints,
        text: texts,
        marker: {
          color: colors,
        },
        type: 'scatter',
        mode: 'markers',
      },
    ];
    var layout = {
      title: 'Computed Magnitudes vs. Catalog Magnitudes',
      xaxis: {
        title: 'Standard Catalog Mag',
      },
      yaxis: {
        title: type === 'instrumental' ? 'Instrumental Mag' : 'Standard Mag (computed)',
      },
      hovermode: 'closest',
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
