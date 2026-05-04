# DIRAC - Business Intelligence Agents

MkDocs documentation repo for DIRAC BIA topics, with current emphasis on
monitoring, logging, metrics, dashboards, IT systems visibility, and repo-local
ADR proposals.

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Install

```bash
pip install -r requirements.txt
```

### Serve

```bash
mkdocs serve
```

### Strict Build

```bash
python -m mkdocs build --strict -f D:\github\dirac-bia\mkdocs.yml
```

## Repo Layout

```text
docs/
  adr/                 ADR proposals and decisions for dirac-bia
  monitoring-areas/    Monitoring, logs, metrics, and alerting docs
  influxdb-dashboards/ Dashboard documentation
  4-it-systems/        IT systems intelligence scope
  agent/               Repo-local MCP entrypoints
  context/             Repo capabilities, workflows, and contracts
mkdocs.yml             MkDocs configuration
overrides/             Theme overrides
hooks/                 Build hooks
```

## Maintenance

- Edit Markdown sources in `docs/`.
- Update `mkdocs.yml` when navigation changes.
- Keep `.docs-template-info.json` in normalized state.
- Refresh workspace MCP metadata when repo context changes.

## Utilities

```bash
mkdocs-oves-krr
mkdocs-oves-render
```
