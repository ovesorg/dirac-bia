# Workflows

## Update Repo Documentation

1. Edit the relevant Markdown sources under `docs/`
2. Update `mkdocs.yml` when navigation or page structure changes
3. Update `docs/adr/` when the change introduces or revises a repo-local architecture proposal or decision
4. Validate with `python -m mkdocs build --strict -f D:\github\dirac-bia\mkdocs.yml`
5. Review whether changes should also update repo MCP context docs

## Provision Or Refresh Repo MCP Docs

1. Run `python D:\github\workspace-mcp\scripts\mcp_provision.py dirac-bia`
2. Preserve repo-authored MCP files unless a reset is explicitly intended
3. Refine `docs/agent/*` and `docs/context/*` to match the actual repo scope
4. Confirm `dirac-bia` appears correctly in `D:\github\workspace-mcp\workspace-repo-registry.generated.json`

## Maintain Curated-Docs Readiness

1. Keep `.docs-template-info.json` in normalized state
2. Keep hub integration enabled in `mkdocs.yml`
3. Avoid broken nav entries or dead internal links
4. Rebuild locally before treating the repo as curation-ready
