#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compile all TikZ .tex files and export PDF -> PNG.

Usage:
    python compile_tikz.py --dir ./动画与图/TikZ --dpi 220
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile TikZ figures and export PNG")
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--dpi", type=int, default=220)
    ap.add_argument("--engine", default="xelatex")
    ap.add_argument("--keep-logs", action="store_true")
    args = ap.parse_args()

    root = args.dir.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    engine = shutil.which(args.engine)
    if not engine:
        print(f"engine not found: {args.engine}")
        return 2

    try:
        import fitz  # PyMuPDF
    except Exception:
        print("PyMuPDF (fitz) not found; cannot export PNG. pip install pymupdf")
        return 2

    tex_files = sorted(root.glob("*.tex"))
    if not tex_files:
        print(f"no .tex files in {root}")
        return 2

    failed = []
    compiled = 0
    exported = 0

    for tex in tex_files:
        print(f"\n=== {tex.name} ===")
        cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", tex.name]
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[FAIL] {tex.name}")
            tail = (r.stdout or "") + "\n" + (r.stderr or "")
            print("\n".join(tail.splitlines()[-25:]))
            failed.append(tex.name)
            continue
        compiled += 1
        pdf = tex.with_suffix(".pdf")
        if not pdf.is_file():
            print(f"[FAIL] pdf not produced: {pdf.name}")
            failed.append(tex.name)
            continue
        png = tex.with_suffix(".png")
        try:
            doc = fitz.open(pdf)
            pix = doc[0].get_pixmap(dpi=args.dpi, alpha=False)
            pix.save(png)
            exported += 1
            print(f"[OK] {tex.name} -> {png.name} ({pix.width}x{pix.height})")
        except Exception as exc:
            print(f"[FAIL] export {png.name}: {exc}")
            failed.append(tex.name)

    if not args.keep_logs:
        for p in root.glob("*.aux"):
            p.unlink(missing_ok=True)
        for p in root.glob("*.log"):
            p.unlink(missing_ok=True)
        for p in root.glob("*.out"):
            p.unlink(missing_ok=True)

    print("\n" + "=" * 60)
    print(f"compiled: {compiled}/{len(tex_files)}  exported: {exported}/{len(tex_files)}")
    if failed:
        print("failed:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
