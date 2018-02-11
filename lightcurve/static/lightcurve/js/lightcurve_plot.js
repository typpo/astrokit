function loadData() {
  $.get('/lightcurve/' + window.lightcurveId + '/plot_json', function(data) {
    console.log(data.reductions);
    plot(data.reductions);
  });
}

function getChartForStandard(reductions) {
  return [
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
}

function getChartForInstrumental(reductions) {
  return [
    {
      x: reductions.map(function(r) { return r.timestamp }),
      y: reductions.map(function(r) { return r.result.mag_instrumental }),
      type: 'scatter',
      mode: 'markers',
    },
  ];
}

function getChart(reduction) {
  return getChartType() === 'instrumental' ?
          getChartForInstrumental(reduction) : getChartForStandard(reduction);
}

function getChartYAxisLabel() {
  // FIXME(ian): Pass in this info from the light curve...
  return getChartType() === 'instrumental' ?
              'Magnitude (' + 'b' + ')' :
              'Magnitude (' + 'B' + ')';
}

function getChartType() {
  var url = new URL(window.location.href);
  return url.searchParams.get('type') || 'standard';
}

function plot(reductions) {
  var chart = getChart(reductions);
  var layout = {
    title: window.lightcurveName,
    xaxis: {
      title: 'Date',
    },
    yaxis: {
      title: getChartYAxisLabel(),
    },
  };

  Plotly.newPlot('plot-container', chart, layout);
}

$(function() {
  loadData();
});
