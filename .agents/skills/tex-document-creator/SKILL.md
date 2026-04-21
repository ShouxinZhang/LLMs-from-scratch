---
name: tex-document-creator
description: 创建或修改 TeX/LaTeX 文档。适用于新建中文笔记、讲义、报告、幻灯片，或整理 TeX 目录结构，特别是需要把 tex、pdf、build 分开的任务。
---

# TeX Document Creator

用于仓库内的 TeX 文档创建、改写、编译和目录整理。

## 默认做法

- 先看仓库里是否已有 `.tex`、`latexmkrc`、`Makefile`、`compile.sh` 等约定；有就复用。
- 中文文档默认用 `ctexart`；长文档可用 `ctexrep`；幻灯片可用 `ctexbeamer`。
- 预设最小前导区，不堆无关宏包。
- 目录默认保持：

```text
文档目录/
├── xxx.tex
├── xxx.pdf
└── build/
```

- `aux/log/out/toc/fls/fdb_latexmk/synctex.gz/xdv` 之类中间文件放进 `build/`。
- 如需编译脚本，放在 `build/compile.sh`，不要把顶层弄乱。

## 图形与宏包

- 如果文档里有多张几何直观图，先检查是否已有合适宏包，不要默认全手写 TikZ。
- 可先用 `kpsewhich` 探测本机是否有现成包，例如：
  - `tkz-euclide`：平面几何、坐标点、角、直角标记；
  - `pgfplots`：坐标图、函数图、数据图。
- 只有在没有合适包，或需求明显超出包的舒适区时，才自己造轮子。
- 如果必须手写 TikZ，至少抽出统一样式，避免整份文档里线宽、箭头、颜色、标签位置各写各的。
- 教学型文档不要只写文字不给图；应在“读者需要脑补图形”的位置主动补图。

## 编译

- 优先 `latexmk -xelatex -outdir=build`
- 如有需要，把最终 PDF 拷回文档目录顶层
- 若 `latexmk` 不可用，再退回 `xelatex -output-directory`

## 写作要求

- 若任务是“通俗解释论文/方法”，优先参考 `references/research-paper-simplifier.md`。
- 若任务是“解释一个技术方法并保留推导”，再参考 `references/method-note-writing.md`。
- 非必要不解释 LaTeX 常识；把上下文留给具体任务。
- `hyperref` 开着时，标题里尽量不要直接塞复杂数学公式。
- 若文档使用 `\tableofcontents`，目录页后默认显式加 `\newpage`，避免正文紧接在目录后面。
- 若用户明确要求某种结构化环境块（如 `Problem`、`Definition`、`Theorem`、`Proof`），应在前导区一次性设计好，而不是正文里零散凑出来。
- 若文档是入门讲义，优先保证版面和叙述的一致性，而不是追求花哨宏包堆叠。
- 图较多时，先列出图清单，再分批编译；不要等全文写完才发现图形风格失控。

## 资源

- 新建脚手架：`scripts/scaffold_tex_document.sh`
- 补充约定：`references/layout-and-build.md`
- 论文通俗解释风格：`references/research-paper-simplifier.md`
- 方法型技术笔记写法：`references/method-note-writing.md`
