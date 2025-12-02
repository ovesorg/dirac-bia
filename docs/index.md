# Welcome to Your Project

This is your documentation homepage.

## Quick Start

Start editing your documentation by modifying the Markdown files in the `docs/` directory.

## Features

- Built with MkDocs and Material theme
- OVES branding and customization
- Authentication support
- PlantUML diagram rendering
- Multi-format charting (Chart.js, matplotlib, Graphviz)
- KRR utility for clean rebuilds

## Chart Capabilities

This template includes three powerful charting options:

### Interactive Charts (Chart.js)

<canvas id="sampleChart" width="600" height="250" data-chart='{
  "type": "bar",
  "data": {
    "labels": ["Product A", "Product B", "Product C", "Product D"],
    "datasets": [{
      "label": "Q4 Sales ($K)",
      "data": [65, 59, 80, 45],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(75, 192, 192, 0.8)"
      ]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {"display": true, "text": "Product Sales", "font": {"size": 16}},
      "legend": {"display": false}
    },
    "scales": {
      "y": {"beginAtZero": true, "title": {"display": true, "text": "Sales (Thousands)"}}
    }
  }
}'></canvas>

**Interactive browser charts** - Add `<canvas>` with JSON data, no build step required.

### Static Charts

Run `mkdocs-oves-render` to generate:

- **Python charts** (matplotlib) - Data analytics and metrics
- **DOT diagrams** (Graphviz) - Architecture and flowcharts

## Next Steps

1. Edit `docs/index.md` to update this page
2. Add new pages in the `docs/` directory
3. Update `mkdocs.yml` to configure navigation
4. Run `python -m mkdocs serve` to preview locally
