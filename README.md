# teaching-pack

[![ci](https://github.com/shenself929/teaching-pack/actions/workflows/ci.yml/badge.svg)](https://github.com/shenself929/teaching-pack/actions/workflows/ci.yml)

> 一次性把任意知识主题做成一套可自学的完整教学包。

安装位置（用户级）：

```text
~/.agents/skills/teaching-pack/
```

## 它做什么

输入：论文 / 代码库 / 算法 / 工具 / 规范 / 课程材料 / 任意知识主题。

输出：一套完整的教学包，包含：

- 学习路线与教学规格
- 全局地图 + 基础篇 + 主题篇 + 我的工作篇
- 公式/代码对照、逐行讲解
- TikZ/drawio 正式图、可选 HTML 动画
- 可运行 demo
- 速查卡、自测题与答案
- README 可点击总表、每篇上一节/下一节
- 验收报告

默认 **deep + one-shot**：一次请求交付完整包，不只给提纲。

## 触发示例

- “把这篇论文和官方代码做成一套能自学的完整教学包，配图、demo、自测题。”
- “我想三天学会 Docker/Kubernetes，做成教程，不要只给提纲。”
- “把 A/B/C 三个方法串成一条线，重点讲清我的改进 D 是怎么做出来的。”
- “只给我一小时速览，不要展开成二十篇文档。”

## 不适用

- 单次简短解释
- 整篇论文翻译 → `nature-reader`
- 组会/答辩 PPT → `paper-ppt-deck` / `nature-paper2ppt`
- 单张机制图 → `scientific-schematics` / `markdown-mermaid-writing`

## 目录

```text
teaching-pack/
├── SKILL.md
├── README.md
├── references/
│   ├── pack-blueprints.md
│   ├── source-audit.md
│   ├── teaching-patterns.md
│   ├── visual-language.md
│   ├── quality-gates.md
│   └── test-prompts.md
├── assets/
│   ├── templates/
│   │   ├── README.template.md
│   │   ├── doc.template.md
│   │   ├── code-walkthrough.template.md
│   │   ├── demo-readme.template.md
│   │   └── nav-block.md
│   └── tikz-preamble.tex
└── scripts/
    ├── scaffold_pack.py
    ├── check_pack.py
    └── compile_tikz.py
```

## 使用脚本

### 生成骨架

```bash
python scripts/scaffold_pack.py \
  --root ./彻底学会_XXX \
  --title "彻底学会 XXX" \
  --modules "主题A,主题B,我的工作" \
  --mode deep
```

### 检查链接/图片/导航

```bash
python scripts/check_pack.py --root ./彻底学会_XXX --require-nav --require-readme-index
```

### 编译 TikZ

```bash
python scripts/compile_tikz.py --dir ./彻底学会_XXX/动画与图/TikZ --dpi 220
```

## 安装后测试

skill 注册在会话启动时加载；新建 ZCode 会话后测试：

```text
/skill teaching-pack 把这篇论文和它的代码做成一套完整教学包，一次交付，不要只给提纲。
```

按 `references/test-prompts.md` 的 5 个 prompt 逐个测试。

## 验收基准

验收看的是一套完整教学包的**完整度**，不是某个固定主题：

- 有学习路线、教学规格、全局地图
- 有基础篇 + 每个主题的论文/实现文档
- 有正式图、demo、速查卡、自测题
- 有导航、可点击链接、可点击图片
- 有一次性的验收报告

不要把任何参考成品当内容模板；只把它当完整度基准。

## 已验证

- `scaffold_pack.py`：deep 模式生成 26 个文件，quick 模式生成 5 个文件
- `check_pack.py`：对一套 28 篇 Markdown + 8 个 HTML 的完整教学包检查，0 错误
- `compile_tikz.py`：编译 8/8 张 TikZ，导出 8/8 PNG
- 故障注入：坏链接、坏图片、`\(...\)` 定界符均能被检出并非零退出

## License

MIT

## 版本

0.1.0
