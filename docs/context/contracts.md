# Contracts

## Discovery Contract

- this repo should expose agent-readable context through `docs/agent` and `docs/context`
- repo-local manifest is authoritative when present

## Documentation Contract

- `mkdocs.yml` must reference real pages that exist in `docs/`
- repo docs should build under strict MkDocs mode before being treated as healthy
- monitoring, logging, and metrics pages are repo-local documentation, not executable infrastructure configuration

## Scope Contract

- use this repo for BIA-specific documentation on dashboards, monitoring areas, and IT systems intelligence
- use `dirac-framework` for broader shared DIRAC architectural guidance when the topic extends beyond `dirac-bia`
- do not treat placeholder or empty topic folders as authoritative until they contain real docs

## Curation Contract

- MkDocs template normalization metadata in `.docs-template-info.json` should remain intact
- hub integration settings should stay enabled unless the repo is intentionally removed from curated-doc participation
