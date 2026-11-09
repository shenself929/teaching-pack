#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a teaching pack for broken links, missing images, nav blocks, formula delimiters, and HTML scripts.

Usage:
    python check_pack.py --root ./彻底学会_XXX --require-nav --require-readme-index
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote

EXCLUDE_DIRS = {".git", "outputs", "__pycache__", "node_modules", ".venv", "venv", ".idea"}
LINK_RE = re.compile(r"(!?)\[[^\]]*\]\(([^)]+)\)")
HTML_ATTR_RE = re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
SCRIPT_RE = re.compile(r"<script[^>]*>(.*?)</script>", re.S | re.I)


def iter_files(root: Path, suffix: str):
    for p in root.rglob(f"*{suffix}"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.is_file():
            yield p


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans."""
    out = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        out.append(line)
    return "\n".join(out)


def rel_target(source: Path, target: str) -> Path | None:
    target = unquote(target.strip())
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:", "javascript:")):
        return None
    target = target.split("#", 1)[0].strip()
    if not target:
        return None
    return (source.parent / target).resolve()


def check_markdown(path: Path, root: Path, require_nav: bool):
    text = path.read_text(encoding="utf-8")
    clean = strip_code(text)
    errors, warnings = [], []

    h1 = [ln for ln in clean.splitlines() if ln.startswith("# ")]
    if len(h1) != 1:
        warnings.append(f"H1 count = {len(h1)} (expected 1)")

    if require_nav and path.name != "README.md":
        if "<!-- nav:start -->" not in text:
            errors.append("missing top nav marker")
        if "<!-- nav:start-footer -->" not in text:
            errors.append("missing bottom nav marker")

    # formula delimiters
    if "\\(" in clean or "\\)" in clean:
        errors.append("found \\( \\) math delimiters; use $...$")
    if "\\[" in clean or "\\]" in clean:
        errors.append("found \\[ \\] math delimiters; use $$...$$")
    # dollar count (outside code); ignore escaped \$
    dollars = len(re.findall(r"(?<!\\)\$", clean))
    if dollars % 2:
        warnings.append(f"odd number of $ delimiters ({dollars})")

    # links and images
    for m in LINK_RE.finditer(clean):
        is_image = bool(m.group(1))
        target = rel_target(path, m.group(2))
        if target is None:
            continue
        try:
            target.relative_to(root)
        except ValueError:
            warnings.append(f"link escapes pack root: {m.group(2)}")
            continue
        if not target.exists():
            kind = "image" if is_image else "link"
            errors.append(f"missing {kind}: {m.group(2)}")

    return errors, warnings


def check_html(path: Path, root: Path):
    text = path.read_text(encoding="utf-8")
    errors, warnings = [], []

    for t in HTML_ATTR_RE.findall(text):
        if t.startswith(("#", "http://", "https://", "data:", "javascript:", "mailto:")):
            continue
        target = (path.parent / unquote(t).split("#", 1)[0]).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            warnings.append(f"HTML asset escapes root: {t}")
            continue
        if not target.exists():
            errors.append(f"missing HTML asset: {t}")

    scripts = SCRIPT_RE.findall(text)
    if scripts:
        node = shutil.which("node")
        if node:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write("\n".join(scripts))
                tmp = Path(f.name)
            try:
                r = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True)
                if r.returncode != 0:
                    errors.append(f"node --check failed: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'unknown'}")
            finally:
                tmp.unlink(missing_ok=True)
        else:
            warnings.append("node not found; skipped JS syntax check")

    return errors, warnings


def check_readme_index(root: Path, md_files: list[Path]):
    readme = root / "README.md"
    if not readme.is_file():
        return ["README.md missing"], []
    text = readme.read_text(encoding="utf-8")
    clean = strip_code(text)
    linked = set()
    for m in LINK_RE.finditer(clean):
        target = rel_target(readme, m.group(2))
        if target and target.suffix.lower() == ".md":
            linked.add(target.resolve())
    missing = []
    for p in md_files:
        if p.name == "README.md":
            continue
        if p.resolve() not in linked:
            missing.append(p.relative_to(root).as_posix())
    errors = [f"README index missing: {m}" for m in missing]
    return errors, []


def main() -> int:
    ap = argparse.ArgumentParser(description="Check a teaching pack")
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--require-nav", action="store_true")
    ap.add_argument("--require-readme-index", action="store_true")
    ap.add_argument("--skip-html", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    md_files = sorted(iter_files(root, ".md"))
    html_files = [] if args.skip_html else sorted(iter_files(root, ".html"))

    all_errors, all_warnings = [], []
    per_file = {}

    for p in md_files:
        e, w = check_markdown(p, root, args.require_nav)
        per_file[p.relative_to(root).as_posix()] = {"errors": e, "warnings": w}
        all_errors += [f"{p.relative_to(root).as_posix()}: {x}" for x in e]
        all_warnings += [f"{p.relative_to(root).as_posix()}: {x}" for x in w]

    for p in html_files:
        e, w = check_html(p, root)
        per_file[p.relative_to(root).as_posix()] = {"errors": e, "warnings": w}
        all_errors += [f"{p.relative_to(root).as_posix()}: {x}" for x in e]
        all_warnings += [f"{p.relative_to(root).as_posix()}: {x}" for x in w]

    if args.require_readme_index:
        e, w = check_readme_index(root, md_files)
        all_errors += e
        all_warnings += w

    if args.json:
        print(json.dumps({
            "root": str(root),
            "markdown": len(md_files),
            "html": len(html_files),
            "errors": all_errors,
            "warnings": all_warnings,
            "files": per_file,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print(f"root: {root}")
        print(f"markdown: {len(md_files)}  html: {len(html_files)}")
        print(f"errors: {len(all_errors)}  warnings: {len(all_warnings)}")
        print("-" * 70)
        for x in all_errors:
            print(f"[ERROR] {x}")
        for x in all_warnings:
            print(f"[WARN ] {x}")
        print("=" * 70)

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
