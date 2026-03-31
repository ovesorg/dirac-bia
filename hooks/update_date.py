"""
MkDocs hook to automatically update editorial build metadata on build.
"""
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path


def on_config(config):
    """Update editorial date and build hash on every build."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    current_date = now.strftime("%Y-%m-%d")
    repo_name = Path(config.config_file_path).resolve().parent.name
    build_hash = sha1(f"{timestamp}:{repo_name}".encode("utf-8")).hexdigest()[:6]

    config["extra"]["oves_revision_date"] = current_date
    config["extra"]["oves_build_hash"] = build_hash
    return config
