"""Verify published source hashes, Python syntax, local links and obvious secrets.

This is a focused publication check, not a comprehensive security scanner.
It never prints credential values.
"""

import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def verify():
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    sources = {s["path"]: s for s in manifest["sources"]}
    errors, checked, links = [], 0, 0
    for asset in manifest["published_assets"]:
        file = ROOT / asset["path"]
        expected = asset.get("published_sha256", sources[asset["source"]]["sha256"])
        if asset.get("published_sha256") and not asset.get("transformation"):
            errors.append(asset["path"] + ": undocumented transformation")
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            errors.append(asset["path"] + ": source hash mismatch")
        for alias in asset.get("equivalent_sources", []):
            if sources[alias]["sha256"] != sources[asset["source"]]["sha256"]:
                errors.append(asset["path"] + ": non-identical source alias")
    patterns = [r"\b(?:sk-|ghp_|hf_)[A-Za-z0-9_-]{15,}",
                r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                r"/(?:Users|Volumes)/[^\s]+"]
    for file in ROOT.rglob("*"):
        if not file.is_file() or any(x in file.relative_to(ROOT).parts for x in (".git", "outputs", ".venv", "__pycache__")):
            continue
        checked += 1
        if file.suffix == ".xlsx":
            with ZipFile(file) as workbook:
                for name in workbook.namelist():
                    if name.endswith((".xml", ".rels")):
                        content = workbook.read(name).decode("utf-8")
                        if any(re.search(p, content) for p in patterns):
                            errors.append(str(file.relative_to(ROOT)) + ": potential secret or private path in workbook")
                        if 'TargetMode="External"' in content or 'x15ac:absPath' in content:
                            errors.append(str(file.relative_to(ROOT)) + ": external relationship or absolute save path")
                    if "vbaProject" in name or name.startswith(("xl/externalLinks/", "xl/embeddings/")):
                        errors.append(str(file.relative_to(ROOT)) + ": active or embedded workbook content")
            continue
        if file.suffix not in (".py", ".md", ".json", ".txt", ".yml", ".example", ".html", ".js", ".mjs", ".ipynb"):
            continue
        text = file.read_text(encoding="utf-8")
        relative = str(file.relative_to(ROOT))
        if any(re.search(p, text) for p in patterns):
            errors.append(relative + ": potential secret or private path")
        if file.suffix == ".py":
            ast.parse(text, filename=relative)
        if file.suffix in (".json", ".ipynb"):
            json.loads(text)
        if file.suffix == ".md":
            if re.search(r"[\u4e00-\u9fff]", text):
                errors.append(relative + ": non-English explanatory text")
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                links += 1
                resolved = (file.parent / unquote(target.split("#", 1)[0])).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    errors.append(relative + ": broken local link")
    return dict(files_checked=checked, local_links_checked=links, source_records=len(sources), errors=errors)


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
