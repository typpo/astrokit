function loadData() {
  $.get('/lightcurve/' + window.lightcurveId + '/plot_json', function(data) {
    console.log(data.reductions);
    plot(data.reductions);
  });
}

function plot(reductions) {
  var chart = [
    {
      x: reductions.map(function(r) { return r.timestamp }),
      y: reductions.map(function(r) { return r.result.mag_standard }),
      error_y: {
        type: 'data',
        visible: true,
        array: reductions.map(function(r) { return r.result.mag_std }),
      },
      type: 'scatter',
      mode: 'markers',
    },
  ];

  var layout = {
    title: window.lightcurveName,
    xaxis: {
      title: 'Date',
    },
    yaxis: {
      // FIXME(ian): Pass in this info from the light curve...
      title: 'Magnitude (' + 'B' + ')',
    },
  };

  Plotly.newPlot('plot-container', chart, layout);
}

$(function() {
  loadData();
});
