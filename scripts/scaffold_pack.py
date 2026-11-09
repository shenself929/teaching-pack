#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scaffold a teaching pack.

Usage:
    python scaffold_pack.py --root ./彻底学会_XXX --title "彻底学会 XXX" \
        --modules "主题A,主题B,我的工作" --mode deep
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"


def write(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"skip existing: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"write: {path}")


def read_template(name: str) -> str:
    p = TEMPLATES / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a teaching pack")
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--title", required=True)
    ap.add_argument("--modules", default="主题A,主题B,我的工作",
                    help="comma separated module names")
    ap.add_argument("--mode", choices=["quick", "standard", "deep"], default="deep")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    root: Path = args.root
    root.mkdir(parents=True, exist_ok=True)

    modules = [m.strip() for m in args.modules.split(",") if m.strip() and m.strip() != "基础"]
    if args.mode == "quick":
        dirs = ["图"]
    else:
        dirs = ["01_基础篇", "06_动手实验", "07_速查卡", "动画与图/TikZ", "动画与图/drawio"]
        for i, m in enumerate(modules, start=2):
            dirs.append(f"{i:02d}_{m}")
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    # Placeholder docs (so the scaffold has the same shape as the README)
    doc_rows = []
    if args.mode == "quick":
        for f in ["00_一页纸.md", "01_核心概念.md", "02_最小例子.md", "03_自测20题.md"]:
            doc_rows.append(f"| 速览 | [{f[:-3]}]({f}) | 待填写 |")
    else:
        doc_rows = ["| 入门 | [全局地图](00_全局地图.md) | 一条主线 |",
                    "| 入门 | [教学规格](00_教学规格.md) | 学习者/目标/评估 |"]
        # base docs
        for f in ["01_基础篇/01_先修A.md", "01_基础篇/02_先修B.md"]:
            doc_rows.append(f"| 基础 | [{Path(f).stem}]({f}) | 待填写 |")
        for i, m in enumerate(modules, start=2):
            if ("我的工作" in m) or ("项目" in m) or (m.lower() == "project"):
                files = ["00_研究故事.md", "01_方法与公式.md", "02_代码地图.md",
                         "03_实验设计.md", "04_结果怎么读.md", "05_论文写作.md",
                         "06_踩坑与纠错.md", "07_一页纸.md"]
            else:
                files = ["00_一页纸.md", "01_论文精讲.md", "02_代码逐行.md"]
            for f in files:
                rel = f"{i:02d}_{m}/{f}"
                doc_rows.append(f"| {m} | [{Path(f).stem}]({rel}) | 待填写 |")
        doc_rows.append("| 实验 | [动手实验](06_动手实验/README_怎么跑.md) | 待填写 |")
        for f in ["07_速查卡/公式速查.md", "07_速查卡/代码入口速查.md", "07_速查卡/术语表.md", "07_速查卡/自测60题.md"]:
            doc_rows.append(f"| 速查 | [{Path(f).stem}]({f}) | 待填写 |")

    # README
    if args.mode == "quick":
        tree = "\n".join([
            f"{root.name}/",
            "├── README.md",
            "├── 00_一页纸.md",
            "├── 01_核心概念.md",
            "├── 02_最小例子.md",
            "├── 03_自测20题.md",
            "└── 图/",
        ])
    else:
        tree_lines = [
            f"{root.name}/",
            "├── README.md",
            "├── 00_教学规格.md",
            "├── 00_全局地图.md",
            "├── 01_基础篇/",
        ]
        for i, m in enumerate(modules, start=2):
            tree_lines.append(f"├── {i:02d}_{m}/")
            if ("我的工作" in m) or ("项目" in m) or (m.lower() == "project"):
                tree_lines += [
                    "│   ├── 00_研究故事.md",
                    "│   ├── 01_方法与公式.md",
                    "│   ├── 02_代码地图.md",
                    "│   ├── 03_实验设计.md",
                    "│   ├── 04_结果怎么读.md",
                    "│   ├── 05_论文写作.md",
                    "│   ├── 06_踩坑与纠错.md",
                    "│   └── 07_一页纸.md",
                ]
            else:
                tree_lines += [
                    "│   ├── 00_一页纸.md",
                    "│   ├── 01_论文精讲.md",
                    "│   └── 02_代码逐行.md",
                ]
        tree_lines += [
            "├── 06_动手实验/",
            "├── 07_速查卡/",
            "└── 动画与图/",
            "    ├── TikZ/",
            "    └── drawio/",
        ]
        tree = "\n".join(tree_lines)

    readme = read_template("README.template.md")
    replacements = {
        "{{TITLE}}": args.title,
        "{{SUBTITLE}}": "一套可自学的完整教学包：先看路线，再读讲义，最后动手验证。",
        "{{LEARNER}}": "待填写：新手 / 实践者 / 研究者",
        "{{OUTCOMES}}": "待填写：学完能解释、能推导、能实现、能诊断什么",
        "{{ROUTES}}": "quick / standard / deep",
        "{{TIME}}": "待填写",
        "{{QUICK_TIME}}": "1–3 小时",
        "{{STANDARD_TIME}}": "2–3 天",
        "{{DEEP_TIME}}": "1–2 周",
        "{{QUICK_ROUTE}}": "待填写",
        "{{STANDARD_ROUTE}}": "待填写",
        "{{DEEP_ROUTE}}": "待填写",
        "{{DOC_TABLE}}": "| 分类 | 文档 | 一句话 |\n|---|---|---|\n" + "\n".join(doc_rows),
        "{{TREE}}": tree,
        "{{VERIFY}}": "python scripts/check_pack.py --root . --require-nav --require-readme-index",
        "{{EXPECTED}}": "broken links: 0\nbroken images: 0\nmissing nav: 0",
        "{{BOUNDARIES}}": "待填写：缺哪些数据、哪些结论未验证、哪些图无法生成。",
    }
    for k, v in replacements.items():
        readme = readme.replace(k, v)
    write(root / "README.md", readme, args.force)

    if args.mode == "quick":
        for name, title in [
            ("00_一页纸.md", "一页纸"),
            ("01_核心概念.md", "核心概念"),
            ("02_最小例子.md", "最小例子"),
            ("03_自测20题.md", "自测 20 题"),
        ]:
            write(root / name, f"# {title}\n\n> 待填写。\n", args.force)
    else:
        write(root / "00_教学规格.md", """# 教学规格

> 先定学习者、目标、先修和评估，再写正文。

## 学习者

- 类型：
- 已有基础：
- 主要缺口：

## 学习目标

- 能解释：
- 能推导：
- 能实现：
- 能诊断：

## 先修

1.
2.
3.

## 概念依赖

```text
A → B → C
```

## 目标 ↔ 文档 ↔ 练习 ↔ 评估

| 目标 | 文档 | 例子/demo | 练习 | 评估 |
|---|---|---|---|---|
| | | | | |
""", args.force)
        write(root / "00_全局地图.md", """# 全局地图

> 一条主线 + 每个模块解决什么。

## 1. 一句话

## 2. 模块关系

```text
模块 A → 模块 B → 模块 C
```

## 3. 学习顺序

1.
2.
3.
""", args.force)
        for f in ["01_基础篇/01_先修A.md", "01_基础篇/02_先修B.md"]:
            write(root / f, "# " + Path(f).stem + "\n\n> 待填写。\n", args.force)
        for i, m in enumerate(modules, start=2):
            if ("我的工作" in m) or ("项目" in m) or (m.lower() == "project"):
                items = [("00_研究故事.md", "研究故事"), ("01_方法与公式.md", "方法与公式"),
                         ("02_代码地图.md", "代码地图"), ("03_实验设计.md", "实验设计"),
                         ("04_结果怎么读.md", "结果怎么读"), ("05_论文写作.md", "论文写作"),
                         ("06_踩坑与纠错.md", "踩坑与纠错"), ("07_一页纸.md", "一页纸")]
            else:
                items = [("00_一页纸.md", "一页纸"), ("01_论文精讲.md", "论文精讲"), ("02_代码逐行.md", "代码逐行")]
            for f, t in items:
                write(root / f"{i:02d}_{m}" / f, "# " + t + "\n\n> 待填写。\n", args.force)
        write(root / "06_动手实验/README_怎么跑.md", """# 动手实验

## 环境

```bash
pip install -r requirements.txt
```

## demo 列表

| demo | 验证什么 | 命令 |
|---|---|---|
| demo1 | | `python demo1_*.py` |
""", args.force)
        write(root / "06_动手实验/requirements.txt", "numpy\nmatplotlib\n", args.force)
        write(root / "07_速查卡/公式速查.md", "# 公式速查\n\n> 待填写。\n", args.force)
        write(root / "07_速查卡/代码入口速查.md", "# 代码入口速查\n\n> 待填写。\n", args.force)
        write(root / "07_速查卡/术语表.md", "# 术语表\n\n> 待填写。\n", args.force)
        write(root / "07_速查卡/自测60题.md", "# 自测 60 题\n\n> 待填写。\n", args.force)
        write(root / "动画与图/README.md", "# 动画与图\n\nTikZ 源在 `TikZ/`，drawio 源在 `drawio/`。\n", args.force)

    print(f"\nscaffold done: {root.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
