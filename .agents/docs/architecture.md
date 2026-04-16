# Repository Architecture

这个仓库不是典型的 Web 服务或单体应用，而是一本书的配套代码库。核心组织方式不是“按业务模块分层”，而是“按学习阶段递进”。

## 整体分层

1. `setup/`
环境安装与运行说明，不承载核心模型逻辑。

2. `ch01` 到 `ch07`
主线章节代码。每章通常包含：
- `01_main-chapter-code/`：该章主代码、脚本入口、测试、Notebook。
- 其他 `bonus` / 专题目录：该章的扩展实验或变体实现。

3. `appendix-*`
附录内容，主要是 PyTorch 基础、训练增强、LoRA、习题答案等补充材料。

4. `pkg/llms_from_scratch/`
可安装的 Python 包。把各章里较稳定的实现抽出为统一 import 接口，便于复用和测试。

5. `reasoning-from-scratch/`
相对独立的后续子项目，主题从 LLM 基础实现延伸到 reasoning、评测、RL 等。

6. `.github/`
CI、工作流和仓库维护脚本。

## 主线代码流

主线基本沿着一本“从零实现 GPT”的路径展开：

- `ch02`：文本切分、tokenization、dataset、dataloader。
- `ch03`：attention / multi-head attention。
- `ch04`：拼装 `GPTModel`，形成最小可运行模型。
- `ch05`：预训练、采样生成、权重加载、训练技巧与模型变体。
- `ch06`：把 GPT 改造成分类微调流程。
- `ch07`：指令微调、数据构造、评测、偏好优化相关实验。

如果只看最关键入口，可优先读：

- `ch04/01_main-chapter-code/gpt.py`
- `ch05/01_main-chapter-code/gpt_train.py`
- `ch06/01_main-chapter-code/gpt_class_finetune.py`
- `ch07/01_main-chapter-code/gpt_instruction_finetuning.py`

## 代码组织特点

- Notebook 是主要载体，脚本文件通常是章节内容的“精简可运行版”。
- 后续章节经常通过 `previous_chapters.py` 复用前面章节的实现，体现教学递进关系。
- `pkg/llms_from_scratch/` 是对章节代码的工程化收口，不是仓库唯一真实来源。
- `kv_cache`、`llama3`、`qwen3` 等目录属于主线之外的可复用扩展实现。
- 很多 bonus 目录是专题实验，和主线并列，不必按生产依赖理解。

## 如何理解这个仓库

可以把它看成三层：

- 学习主线：`ch02` 到 `ch07`
- 工程化复用层：`pkg/llms_from_scratch/`
- 扩展与后续研究：各章 bonus 目录 + `reasoning-from-scratch/`

因此，阅读时最合适的方式不是自顶向下追服务调用，而是按章节追“能力如何逐步叠加”。  
从架构角度看，`ch04` 是模型核心，`ch05` 之后都是围绕训练、加载、微调、评测和变体的外扩。
