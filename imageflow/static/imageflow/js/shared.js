function plotImage(canvas, imageUrl) {
  // First, write the original image to canvas.
  var ctx = canvas.getContext('2d');
  var img = new Image();
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0, img.width, img.height,
                       0, 0, canvas.width, canvas.height);

    // Then plot stars from the data source.
    if (window.catalogData) {
      plotStars(canvas, window.catalogData, {
        color: 'red',
        radius: 6,
        text: function(star) {
          return star.designation;
        }
      });
    }
    if (window.pointSourceData) {
      plotStars(canvas, window.pointSourceData, {
        color: 'green',
        radius: 4,
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
    radius: 5,
    text: function(star) { return star.id },
  }, rawOpts);
  for (var i=0; i < stars.length; i++) {
    var star = stars[i];

    // Plot catalog stars over an image.
    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    // Circle - defined by x, y, radius, ...
    ctx.arc(star.field_x, star.field_y, opts.radius, 0, Math.PI * 2);
    ctx.strokeStyle = star.id === window.targetId ? 'cyan' : opts.color;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Label
    var text = opts.text(star);
    if (!text) {
      continue;
    }

    ctx.font = '14px Arial';
    ctx.strokeStyle= 'black';
    ctx.lineWidth = 4;
    var labelWidth = ctx.measureText(text).width;
    ctx.strokeText(text, star.field_x - (labelWidth / 2), star.field_y - 8);
    ctx.fillStyle = 'yellow';
    ctx.fillText(text, star.field_x - (labelWidth / 2), star.field_y - 8);
  }
}

function setupCanvasListeners(canvas) {
  var xPosElt = document.getElementById('canvas-x-pos');
  var yPosElt = document.getElementById('canvas-y-pos');
  canvas.onmousemove = function onMouseover(e) {
    // https://stackoverflow.com/questions/17130395/real-mouse-position-in-canvas
    var rect = canvas.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    xPosElt.innerHTML = parseInt(mx, 10);
    yPosElt.innerHTML = parseInt(my, 10);
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
          return type === 'instrumental' ? r[window.urat1Key] : r.mag_standard;
        }),
        y: yData.map(function(r) { return r.mag_instrumental }),
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
    setupCanvasListeners(canvas);
    plotImage(canvas, window.originalImageUrl);
  }

  setupTables();
  setupNotes();

  // Initialize tooltips.
  if ($().tooltip) {
    $('[data-toggle="tooltip"]').tooltip({container: 'body'})
  }
});
