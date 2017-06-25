function plotImage(canvas, imageUrl) {
  // First, write the original image to canvas.
  var ctx = canvas.getContext('2d');
  var img = new Image();
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0, img.width, img.height,
                       0, 0, canvas.width, canvas.height);

    // Then plot stars from the catalog.
    plotCatalogStars(canvas, window.catalogReferenceStars);
  };
  img.src = imageUrl;
}

function plotCatalogStars(canvas, referenceStars) {
  for (var i=0; i < referenceStars.length; i++) {
    var star = referenceStars[i];

    // Plot catalog stars over an image.
    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    // Circle - defined by x, y, radius, ...
    ctx.arc(star.field_x, star.field_y, 5, 0, Math.PI * 2);
    ctx.strokeStyle = 'yellow';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Label
    ctx.font = '16px Arial';
    ctx.strokeStyle= 'black';
    ctx.lineWidth = 2;
    var labelWidth = ctx.measureText(star.designation).width;
    ctx.strokeText(star.designation, star.field_x - (labelWidth / 2), star.field_y - 8);
    ctx.fillStyle = 'yellow';
    ctx.fillText(star.designation, star.field_x - (labelWidth / 2), star.field_y - 8);
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
    xPosElt.innerHTML = mx;
    yPosElt.innerHTML = my;
  }
}

(function() {
  var canvas = document.getElementById('reference-star-plot');
  setupCanvasListeners(canvas);
  plotImage(canvas, window.originalImageUrl);

  // Initialize tooltips.
  $('[data-toggle="tooltip"]').tooltip()
})();
