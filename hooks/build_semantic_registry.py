from __future__ import annotations

import json
import re
from pathlib import Path


MARKDOWN_SUFFIXES = {".md", ".markdown"}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
HTML_TAG_RE = re.compile(r"<[^>]+>")
TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
WS_RE = re.compile(r"\s+")
OUTPUT_NAME = "semantic-doc-registry.json"


def on_post_build(config, **kwargs):
    repo_root = Path(config.config_file_path).resolve().parent
    docs_dir = Path(config["docs_dir"]).resolve()
    site_dir = Path(config["site_dir"]).resolve()
    repo_name = repo_root.name
    site_name = config.get("site_name") or repo_name
    base_url = f"https://docs.omnivoltaic.com/internal/{repo_name}/"
    exclude_patterns = parse_exclude_docs(config.get("exclude_docs"))

    sections = []
    for doc_path in sorted(docs_dir.rglob("*")):
        if not doc_path.is_file() or doc_path.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        rel_path = doc_path.relative_to(docs_dir).as_posix()
        if is_excluded(rel_path, exclude_patterns):
            continue
        sections.extend(extract_sections(doc_path.read_text(encoding="utf-8"), rel_path, base_url))

    terms = extract_glossary_terms(docs_dir, base_url)

    payload = {
        "schema_version": 1,
        "repo": repo_name,
        "site_name": site_name,
        "base_url": base_url,
        "generated_at": config.get("extra", {}).get("oves_revision_date"),
        "terms": terms,
        "sections": sections,
    }

    output_path = site_dir / "assets" / OUTPUT_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_sections(text: str, rel_path: str, base_url: str) -> list[dict]:
    text = strip_front_matter(text)
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        plain = normalize_text(text)
        title = title_from_path(rel_path)
        url = build_doc_url(base_url, rel_path)
        return [{
            "ref": f"{rel_path}#",
            "path": rel_path,
            "page_title": title,
            "section_title": title,
            "anchor": "",
            "url": url,
            "excerpt": plain[:240],
            "text": plain[:4000],
        }]

    sections = []
    page_title = clean_inline(matches[0].group(2))
    seen_anchors: dict[str, int] = {}
    for index, match in enumerate(matches):
        heading = clean_inline(match.group(2))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = normalize_text(text[start:end])
        anchor = unique_anchor(slugify(heading), seen_anchors)
        url = build_doc_url(base_url, rel_path, anchor)
        excerpt = body[:240] if body else heading
        sections.append({
            "ref": f"{rel_path}#{anchor}",
            "path": rel_path,
            "page_title": page_title,
            "section_title": heading,
            "anchor": anchor,
            "url": url,
            "excerpt": excerpt,
            "text": body[:4000],
        })
    return sections


def extract_glossary_terms(docs_dir: Path, base_url: str) -> list[dict]:
    glossary_path = docs_dir / "9-appendix" / "1-glossary.md"
    if not glossary_path.exists():
        return []
    lines = strip_front_matter(glossary_path.read_text(encoding="utf-8")).splitlines()
    url = build_doc_url(base_url, "9-appendix/1-glossary.md")
    terms = []
    for line in lines:
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [clean_inline(cell) for cell in match.group(1).split("|")]
        if len(cells) < 2:
            continue
        term = cells[0].strip()
        definition = cells[1].strip()
        if not term or term.lower() == "term":
            continue
        if re.fullmatch(r"-+", term) and re.fullmatch(r"-+", definition):
            continue
        aliases = []
        if "(" in term and ")" in term:
            alias = term.split("(", 1)[0].strip()
            acronym = term.split("(", 1)[1].split(")", 1)[0].strip()
            if alias:
                aliases.append(alias)
            if acronym:
                aliases.append(acronym)
        terms.append({
            "term": term,
            "normalized": slugify(term).replace("-", " "),
            "aliases": sorted(set(a for a in aliases if a and a != term)),
            "definition": definition,
            "section_refs": ["9-appendix/1-glossary.md#"],
            "url": url,
        })
    return terms


def build_doc_url(base_url: str, rel_path: str, anchor: str | None = None) -> str:
    pure = Path(rel_path)
    if pure.name == "index.md":
        route = pure.parent.as_posix()
    else:
        route = pure.with_suffix("").as_posix() + "/"
    route = route.strip("/")
    url = base_url if not route else base_url.rstrip("/") + "/" + route + "/"
    if anchor:
        url += f"#{anchor}"
    return url


def title_from_path(rel_path: str) -> str:
    stem = Path(rel_path).stem
    return stem.replace("-", " ").replace("_", " ").title()


def strip_front_matter(text: str) -> str:
    return FRONT_MATTER_RE.sub("", text, count=1)


def normalize_text(text: str) -> str:
    text = MARKDOWN_IMAGE_RE.sub(r"\1", text)
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = INLINE_CODE_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub(" ", text)
    text = text.replace("#", " ").replace("*", " ").replace("_", " ").replace("|", " ")
    return WS_RE.sub(" ", text).strip()


def clean_inline(value: str) -> str:
    value = MARKDOWN_LINK_RE.sub(r"\1", value)
    value = INLINE_CODE_RE.sub(r"\1", value)
    value = HTML_TAG_RE.sub(" ", value)
    return WS_RE.sub(" ", value).strip()


def slugify(value: str) -> str:
    value = clean_inline(value).lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value).strip("-")
    return value or "section"


def unique_anchor(anchor: str, seen: dict[str, int]) -> str:
    count = seen.get(anchor, 0)
    seen[anchor] = count + 1
    if count == 0:
        return anchor
    return f"{anchor}_{count}"


def parse_exclude_docs(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def is_excluded(rel_path: str, patterns: list[str]) -> bool:
    path = rel_path.strip("/")
    parts = Path(path).parts
    for pattern in patterns:
        normalized = pattern.strip().replace("\\", "/").strip("/")
        if not normalized:
            continue
        if normalized.startswith("*."):
            if Path(path).match(normalized):
                return True
            continue
        if path == normalized or path.startswith(normalized + "/"):
            return True
        if parts and parts[0] == normalized:
            return True
    return False
