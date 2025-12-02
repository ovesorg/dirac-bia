# DIRAC - Business Impact Analysis

Documentation site built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ovesorg/dirac-bia.git
   cd dirac-bia
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Serve locally**
   ```bash
   mkdocs serve
   ```
   Documentation will be available at http://127.0.0.1:8000

### Build

To build the static site:
```bash
mkdocs build --clean
```

Output will be in the `site/` directory.

## Project Structure

```
.
├── docs/              # Documentation source files
├── overrides/         # Theme customization
│   ├── javascripts/   # Custom JavaScript
│   ├── partials/      # Template overrides
│   └── stylesheets/   # Custom CSS
├── mkdocs.yml         # MkDocs configuration
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Utilities

### KRR (Kill, Rebuild, Restart)

Clean rebuild and restart the documentation server:
```bash
mkdocs-oves-krr
```

### PlantUML Rendering

Render PlantUML diagrams:
```bash
mkdocs-oves-render
```

## Contributing

1. Edit Markdown files in `docs/`
2. Update `mkdocs.yml` for navigation changes
3. Test locally with `mkdocs serve`
4. Commit and push changes

## Support

For issues or questions, please open an issue in this repository.
