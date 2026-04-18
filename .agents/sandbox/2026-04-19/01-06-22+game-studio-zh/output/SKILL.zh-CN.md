---
name: game-studio
description: 为浏览器游戏的早期工作做路由。适用于用户在进入更具体的专项技能前，需要先确定技术栈，并规划设计、实现、美术资产和试玩测试流程的场景。
---

# Game Studio

## 概览

把这个技能作为浏览器游戏工作的总入口。默认走 2D Phaser 路线，除非用户明确要求 3D、Three.js、React Three Fiber、重 shader 渲染，或其他以 WebGL 为优先方向的方案。

这个插件是有意做成不对称的：

- 在 v1 中，2D 是最强的执行路径。
- 3D 只有一套带明确倾向的默认生态：普通 TypeScript 或 Vite 应用默认使用原生 Three.js，React 承载的 3D 应用默认使用 React Three Fiber，GLB 或 glTF 2.0 作为默认的交付资产格式。
- 共享的架构、UI 和试玩测试实践同时适用于这两类方向。

## 在这些情况下使用本技能

- 用户还在选择技术栈
- 请求跨越多个领域，例如运行时、UI、资产流水线和 QA
- 用户只说“帮我做个游戏”，但没有指定实现路径

## 在这些情况下不要停留在这里

- 运行时已经明确是原生 Three.js
- 运行时已经明确是 React Three Fiber
- 任务已经明确是已交付资产的问题
- 任务已经明确只是前端问题或只是 QA 问题

一旦意图清晰，就立刻路由到最具体的专项技能，并从那里继续推进。

## 路由规则

1. 在设计或编码之前，先对请求进行分类：
   - `2D default`：Phaser、精灵、tilemap、俯视角、侧视角、战棋网格、动作平台跳跃等。
   - `3D + plain TS/Vite`：命令式场景控制、类似引擎的循环、非 React 应用、直接使用 Three.js。
   - `3D + React`：由 React 承载的产品界面、声明式场景组合、共享 React 状态、UI 占比高的 3D 应用。
   - `3D asset pipeline`：GLB、glTF、纹理打包、压缩、LOD、运行时资产体积。
   - `Alternative engine`：Babylon.js 或 PlayCanvas 请求，通常是做技术对比或生态适配判断。
   - `Shared`：核心循环设计、前端方向、存档/调试/性能边界、浏览器 QA。
2. 分类后，立即路由到对应的专项技能：
   - 共享架构与引擎选择：`../web-game-foundations/SKILL.md`
   - 深度 2D 实现：`../phaser-2d-game/SKILL.md`
   - 原生 Three.js 实现：`../three-webgl-game/SKILL.md`
   - React 承载的 3D 实现：`../react-three-fiber-game/SKILL.md`
   - 3D 资产交付与优化：`../web-3d-asset-pipeline/SKILL.md`
   - HUD 与菜单方向：`../game-ui-frontend/SKILL.md`
   - 2D 精灵生成与归一化：`../sprite-pipeline/SKILL.md`
   - 浏览器 QA 与视觉检查：`../game-playtest/SKILL.md`
3. 在这些被路由的技能之间保持一套一致的整体方案。不要让引擎、UI、资产和 QA 的决策彼此漂移。

## 默认工作流

1. 先锁定游戏幻想和玩家动作动词。
2. 定义核心循环、失败状态、成长进程，以及目标单局时长。
3. 选择实现路线：
   - 2D 浏览器游戏默认使用 Phaser。
   - 当项目明确是 3D，并且希望在普通 TypeScript 或 Vite 应用中直接控制渲染循环时，选择原生 Three.js。
   - 当项目已经建立在 React 上，或者希望用声明式场景组合并共享 React 状态时，选择 React Three Fiber。
   - 只有当用户明确要求自定义渲染器或 shader-first 界面时，才选择原生 WebGL。
4. 尽早定义 UI 界面层。浏览器游戏通常都需要 DOM HUD 和菜单层，即使游戏主视图是 canvas 或 WebGL。
   - 对于 3D 起步脚手架，默认采用低干扰 HUD，优先保护主游戏视野，并让次级面板保持折叠。
5. 决定资产工作流：
   - 2D 角色和特效：使用 `sprite-pipeline`。
   - 3D 模型、纹理和交付格式：使用 `web-3d-asset-pipeline`。
6. 在宣布工作可投入生产前，先走完一轮试玩测试闭环。

## 输出期望

- 对于规划类请求，返回一份面向具体游戏的方案，包含技术栈选择、玩法循环、UI 界面层、资产工作流和测试方法。
- 对于实现类请求，让所选技术栈在目录结构和代码边界中保持清晰可见。
- 对于混合类请求，保留插件默认策略：除非用户明确要求别的方向，否则优先走 2D Phaser。
- 当用户询问 Babylon.js 或 PlayCanvas 时，要诚实比较，但除非用户明确选择其他引擎，否则仍将 Three.js 和 R3F 作为主要代码生成默认项。

## 参考资料

- 引擎选择：`../../references/engine-selection.md`
- Three.js 技术栈：`../../references/threejs-stack.md`
- React Three Fiber 技术栈：`../../references/react-three-fiber-stack.md`
- 3D 资产流水线：`../../references/web-3d-asset-pipeline.md`
- 原生 Three.js 起步模板：`../../references/threejs-vanilla-starter.md`
- React Three Fiber 起步模板：`../../references/react-three-fiber-starter.md`
- 前端提示词模式：`../../references/frontend-prompts.md`
- 试玩测试清单：`../../references/playtest-checklist.md`

## 示例

- “帮我原型一个浏览器战棋游戏。”
- “我需要一个基于 Phaser 的动作游戏循环，带 HUD 和菜单。”
- “我想做一个 Three.js 探索 Demo，要有 WebGL 光照和适合浏览器的 UI。”
- “我想做一个基于 React 的 3D 配置器，使用 React Three Fiber。”
- “帮我优化面向 Web 的 GLB 资产，并控制文件大小。”
- “帮我搭一套稳定一致的 2D 精灵动画资产工作流。”
