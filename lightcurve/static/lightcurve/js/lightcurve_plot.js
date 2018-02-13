function loadData() {
  var url = '/lightcurve/' + window.lightcurveId +
            '/plot_json?type=' + getChartType();
  $.get(url, function(data) {
    console.log(data.results);
    plot(data.results);
  });
}

function getChartForStandard(results) {
  return [
    {
      x: results.map(function(r) { return r.timestampJd }),
      y: results.map(function(r) { return r.result.mag_standard }),
      error_y: {
        type: 'data',
        visible: true,
        array: results.map(function(r) { return r.result.mag_std }),
      },
      type: 'scatter',
      mode: 'markers',
    },
  ];
}

function getChartForInstrumental(results) {
  return [
    {
      x: results.map(function(r) { return r.timestampJd }),
      y: results.map(function(r) { return r.result.mag_instrumental }),
      type: 'scatter',
      mode: 'markers',
    },
  ];
}

function getChart(results) {
  return getChartType() === 'instrumental' ?
          getChartForInstrumental(results) : getChartForStandard(results);
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

function plot(results) {
  var chart = getChart(results);
  var layout = {
    title: window.lightcurveName,
    xaxis: {
      title: 'Time (Julian Date)',
      exponentformat: 'none',
      separatethousands: false,
      hoverformat: '.5f',
    },
    yaxis: {
      title: getChartYAxisLabel(),
      hoverformat: '.3f',
    },
    separators: '.',
  };

  Plotly.newPlot('plot-container', chart, layout);
}

$(function() {
  loadData();
});
