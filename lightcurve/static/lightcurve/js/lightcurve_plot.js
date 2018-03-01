var plotConfig = {
  period: null,
  lastResults: null,
};

function loadData() {
  var url = '/lightcurve/' + window.lightcurveId +
            '/plot_json?type=' + getChartType();
  $.get(url, function(data) {
    plotConfig.lastResults = data.results;
    plot();
  });
}

function setupListeners() {
  $('#lightcurve-period').on('change', function() {
    plotConfig.period = $(this).val() || null;
    plot();
  });
}

function getTimestampVal(result) {
  if (plotConfig.period) {
    // Fold the lightcurve, if applicable.
    // https://www.southampton.ac.uk/~sdc1g08/BinningFolding.html
    return (result.timestampJd / plotConfig.period) % 1;
  }
  return result.timestampJd;
}

function getChartForStandard(results) {
  return [
    {
      x: results.map(getTimestampVal),
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
      x: results.map(getTimestampVal),
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

function getChartXAxisLabel() {
  if (plotConfig.period) {
    return 'Phase';
  }
  return 'Time (Julian Date)';
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

function plot() {
  var chart = getChart(plotConfig.lastResults);
  var layout = {
    title: window.lightcurveName,
    xaxis: {
      title: getChartXAxisLabel(),
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
  setupListeners();
});
