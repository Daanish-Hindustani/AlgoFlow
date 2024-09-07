document.addEventListener('DOMContentLoaded', function () {
    // Initialize variables
    const chartElement = document.getElementById('chart');
    const loadingElement = document.getElementById('loading');
    const timeframeSelect = document.getElementById('timeframe');
    const chartNameElement = document.getElementById('chart_name');
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.querySelector('.search-input');
    const chartTypeRadios = document.querySelectorAll('input[name="chartType"]');
    const indicatorSeries = {};

    //specifc values from data
    let indicators = [];
    let searchTerm = null;
    let chartType = null;
    let name = null;
    const chart_id = chart_data.chart_id;

    //api data
    let updatedStockData = null;
    //switch between bar and line
    let series = null;


    // Initialization function to fetch initial data
    async function initialize() {
        try {
            timeframeSelect.value = chart_data.interval;
            searchTerm = chart_data.ticker;
            chartType = chart_data.chart_type;
            searchInput.value = searchTerm;
            chartNameElement.value = chart_data.name;
            name = chart_data.name;
            setCheckedRadio(chartTypeRadios, chartType);
            indicators = chart_data.indicators;
            fetchData(searchTerm, timeframeSelect.value);
            setCheckboxes(indicators);
        } catch (error) {
            console.error('Error:', error);
            toggleLoading(false);
        }
    }

    initialize();

    

    // Chart options configuration
    const chartOptions = {
        layout: {
            background: { type: 'solid', color: '#18191a' },
            textColor: 'white',
        },
        grid: {
            vertLines: { color: '#e1e1e1' },
            horzLines: { color: '#e1e1e1' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: '#de73ff',
                style: LightweightCharts.LineStyle.Solid,
                labelBackgroundColor: '#9B7DFF',
                labelFontColor: 'white',
            },
            horzLine: {
                width: 1,
                color: '#9B7DFF',
                labelBackgroundColor: '#9B7DFF',
                labelFontColor: 'white',
            },
        },
    };

    // Create the chart
    const chart = LightweightCharts.createChart(chartElement, chartOptions);
    chart.timeScale().applyOptions({
        borderColor: '#71649C',
        barSpacing: 10,
    });

    // Function to show/hide loading screen
    function toggleLoading(show) {
        loadingElement.style.display = show ? 'block' : 'none';
    }

    // Function to clear all indicator series
    function clearIndicatorSeries() {
        Object.values(indicatorSeries).forEach(series => chart.removeSeries(series));
        Object.keys(indicatorSeries).forEach(key => delete indicatorSeries[key]);
    }

    // Function to fetch data
    async function fetchData(ticker, timeframe) {
        toggleLoading(true);
        try {
            const response = await fetch(`/api/data/${ticker}/${timeframe}`);
            const data = await response.json();

            if (series) {
                chart.removeSeries(series);
            }

            series = chartType === 'bar' ? chart.addCandlestickSeries() : chart.addLineSeries();
            series.setData(data[chartType === 'bar' ? 'candlestick' : 'line']);

            updatedStockData = data;

            clearIndicatorSeries();
            getIndicators().forEach(updateIndicators);

            toggleLoading(false);
        } catch (error) {
            console.error('Error:', error);
            toggleLoading(false);
        }
    }

    // Function to update selected indicators
    async function updateIndicators(indicator) {
        try {
            const response = await fetch(`/api/${indicator}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedStockData['candlestick'])
            });

            const indicatorData = await response.json();

            if (indicatorSeries[indicator]) {
                chart.removeSeries(indicatorSeries[indicator]);
            }

            const color = getRandomColor();
            const series = chart.addLineSeries({ 
                color,
                title: indicator
            });

            series.setData(indicatorData);
            indicatorSeries[indicator] = series;

            series.setMarkers([{
                time: indicatorData[indicatorData.length - 1].time,
                position: 'belowBar',
                shape: 'circle',
                color: color,
                text: indicator,
            }]);
        } catch (error) {
            console.error(`Error sending data to ${indicator} API:`, error);
        }
    }

    // Function to update database
    async function updateDB(chart_id, field, value) {
        try {
            const response = await fetch('/chart/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chart_id: chart_id, field, value })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            chart_data = await response.json();
            console.log('Update successful:', chart_data);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Event listener for chart type
    chartTypeRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            chartType = this.value;
            updateDB(chart_id, "chart_type", chartType);
            fetchData(searchTerm, timeframeSelect.value);
        });
    });

    // Event listener for search button
    searchBtn.addEventListener('click', function () {
        searchTerm = searchInput.value;
        updateDB(chart_id, "ticker", searchTerm);
        fetchData(searchTerm, timeframeSelect.value);
    });

    chartNameElement.addEventListener('change', function (event) {
        event.preventDefault();

        const updatedChartName = chartNameElement.value;
        updateDB(chart_id, "name", updatedChartName);
        name = updatedChartName;
        chartNameElement.value = name;
    });

    // Event listener for timeframe selection
    timeframeSelect.addEventListener('change', function () {
        updateDB(chart_id, "interval", timeframeSelect.value);
        fetchData(searchTerm, timeframeSelect.value);
        console.log(chart_data);
    });

    // Event listener for indicator checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            if (checkbox.checked) {
                indicators.push(checkbox.value);
                updateIndicators(checkbox.value);
            } else {
                if (indicatorSeries[checkbox.value]) {
                    indicators = indicators.filter(item => item !== checkbox.value);
                    chart.removeSeries(indicatorSeries[checkbox.value]);
                    delete indicatorSeries[checkbox.value];
                }
            }
            updateDB(chart_id, 'indicators', indicators);
        });
    });

   // Event listener for option-delete&create
   document.querySelectorAll('#chartcrud .dropdown-item').forEach(function(item) {
    item.addEventListener('click', async function(event) {
      const action = event.target.getAttribute('data-value');
      
      if (action === 'delete') {
        try {
          const response = await fetch('/chart/delete', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ chart_id: chart_id })
          });
          const data = await response.json();
          
          if (data.success) {
            // Reload the page to reflect the deletion
            window.location.href = '/chart/';
          } else {
            console.error('Error:', data.error);
          }
        } catch (error) {
          console.error('Error:', error);
        }
      } else if (action === 'create') {
        try {
          const response = await fetch('/chart/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              ticker: "AAPL",  // Example: default ticker
              interval: "1d",  // Example: default interval
              chart_type: "line",  // Example: default chart type
              indicators: ["ema"]  // Example: default indicators
            })
          });
          
          if (!response.ok) {
            throw new Error('Failed to create chart');
          }
          
          // Get the URL of the newly created chart
          const newChartUrl = response.url;
          
          // Redirect to the newly created chart's page
          window.location.href = newChartUrl;
          
        } catch (error) {
          console.error('Error:', error);
        }
      }
    });
  });
  

    // Utility functions:

    // Function to get selected indicators
    function getIndicators() {
        return Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
    }

    // Function to generate random colors for line series
    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // Function to set the checked radio button based on chart type
    function setCheckedRadio(radioButtons, value) {
        radioButtons.forEach(radio => {
            if (radio.value === value) {
                radio.checked = true;
            }
        });
    }

    // Function to set checkboxes based on indicators
    function setCheckboxes(indicators) {
        indicators.forEach(indicator => {
            const checkbox = document.querySelector(`input[value="${indicator}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }
});
