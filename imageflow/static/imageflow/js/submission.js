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
    ctx.arc(star.field_x, star.field_y, 5, 0, Math.PI * 2, true);
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

plotImage(document.getElementById('reference-star-plot'),
                  window.originalImageUrl);
