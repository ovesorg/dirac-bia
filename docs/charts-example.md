# Charts Example

This page demonstrates the different charting capabilities available in this documentation system.

## Chart.js Interactive Charts

Chart.js provides interactive, responsive charts directly in the browser.

### Line Chart Example

<canvas id="lineChart" width="400" height="200" data-chart='{
  "type": "line",
  "data": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "datasets": [{
      "label": "Revenue 2024",
      "data": [12, 19, 15, 25, 22, 30],
      "borderColor": "rgb(75, 192, 192)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Monthly Revenue Trend"
      }
    }
  }
}'></canvas>

### Bar Chart Example

<canvas id="barChart" width="400" height="200" data-chart='{
  "type": "bar",
  "data": {
    "labels": ["Product A", "Product B", "Product C", "Product D"],
    "datasets": [{
      "label": "Sales Q4 2024",
      "data": [65, 59, 80, 45],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.7)",
        "rgba(54, 162, 235, 0.7)",
        "rgba(255, 206, 86, 0.7)",
        "rgba(75, 192, 192, 0.7)"
      ]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Product Sales Comparison"
      }
    }
  }
}'></canvas>

### Pie Chart Example

<canvas id="pieChart" width="400" height="200" data-chart='{
  "type": "pie",
  "data": {
    "labels": ["Desktop", "Mobile", "Tablet"],
    "datasets": [{
      "data": [55, 35, 10],
      "backgroundColor": [
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 99, 132, 0.8)",
        "rgba(255, 206, 86, 0.8)"
      ]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Traffic by Device Type"
      }
    }
  }
}'></canvas>

## Static Charts (Rendered to PNG)

These charts are pre-rendered to PNG images using Python (matplotlib) or Graphviz (DOT).

### Python Charts (matplotlib)

Run `mkdocs-oves-render` to generate these charts:

#### Performance Metrics
![Performance Chart](diagrams/images/example-performance.png)

#### Sales Analysis
![Sales Chart](diagrams/images/example-sales.png)

### DOT Charts (Graphviz)

Run `mkdocs-oves-render` to generate architecture diagrams:

#### System Architecture
![Architecture Diagram](diagrams/images/example-architecture.png)

## How to Use

### Chart.js (Interactive)

Add a canvas element with a `data-chart` attribute containing JSON configuration:

```html
<canvas id="myChart" data-chart='{
  "type": "line",
  "data": {
    "labels": ["A", "B", "C"],
    "datasets": [{
      "label": "My Data",
      "data": [10, 20, 15]
    }]
  }
}'></canvas>
```

### Python Charts

1. Create a Python script in `docs/diagrams/charts/python/`
2. Use matplotlib or plotly to generate charts
3. Save to `CHART_OUTPUT_DIR` environment variable
4. Run `mkdocs-oves-render` to generate PNGs

### DOT Charts

1. Create a `.dot` file in `docs/diagrams/charts/dot/`
2. Use Graphviz DOT syntax
3. Run `mkdocs-oves-render` to generate PNGs
4. Install Graphviz: https://graphviz.org/download/
