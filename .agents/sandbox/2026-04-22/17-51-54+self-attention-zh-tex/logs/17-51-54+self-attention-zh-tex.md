# Self-Attention 中文零基础讲义任务日志

## 用户原始需求

- 使用 `.agents/skills/zero-base-qa-tutor-zh`
- 启动 `.agents/skills/sandbox-workmode`
- 讲解内容：Lena Voita NLP Course 的 `seq2seq_and_attention.html#self_attention`
- `fetch_web`
- 写 TeX，并构建中文 PDF
- 调用 `image_gen` 工具生成讲解图片，允许生成多张图片

## 执行动作

1. 创建 sandbox 工作区：
   `.agents/sandbox/2026-04-22/17-51-54+self-attention-zh-tex/`
2. 抓取并保存网页 HTML 到 `tmp/`。
3. 使用内置 `image_gen` 生成两张概念图：
   - `images/self_attention_parallel.png`
   - `images/qkv_roles.png`
4. 编写中文 TeX 讲义：
   `tex/self_attention_zero_base_zh.tex`
5. 使用 `latexmk -xelatex` 编译 PDF。
6. 修正 TikZ 流程图横向溢出后重新编译。

## 最终产物

- PDF：`output/self_attention_zero_base_zh.pdf`
- TeX：`tex/self_attention_zero_base_zh.tex`
- 图片：`images/self_attention_parallel.png`、`images/qkv_roles.png`
- 构建脚本：`build/compile.sh`

## 来源

- Lena Voita, NLP Course, Self-Attention 小节：
  https://lena-voita.github.io/nlp_course/seq2seq_and_attention.html#self_attention
