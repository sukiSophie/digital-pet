# Digital-Pet 项目架构与功能指南

本文档旨在为 AI (Gemini/Antigravity) 提供项目的全景视图，阐述各模块的具体功能、组件构成及通信逻辑，以便快速定位和修改代码。

---

## 1. 项目概览
本项目是一个基于 **PyQt6** 开发的具有“自主意识”的可爱风格桌面宠物应用。
- **视觉风格**：半透明、暖色调、圆角设计。深度集成了毛玻璃效果和高级 UI 组件。
- **核心功能**：
    - **桌面陪伴**：图片轮播动画、随机/定向移动、屏幕边缘检测。
    - **自主交互**：**[新]** 彻底去除了传统对话框，改为模型自主触发。模型会根据随机时间或工具调用结果，主动向用户撒娇或改变自身动作状态。
    - **函数调用 (Tool Calling)**：**[新]** 赋予模型感知环境的能力（如时间、天气、用户状态），支持复杂的工具链式交互。
- **技术栈**：Python 3.12+, PyQt6, API 异步调用 (QThread), OpenAI Tool Calling 协议。

---

## 2. 目录结构
```text
Digital-Pet/
├── assets/                 # 资源目录
│   ├── actions/            # 动作文件夹（每个文件夹代表一个动作状态）
│   └── expressions/        # 静态表情/图标
├── src/                    # 源码目录
│   ├── main.py             # 入口程序：初始化、加载配置、设置托盘
│   ├── pet_widget.py       # 核心组件：自主意识大脑、动画控制、状态切换、右键菜单
│   ├── chat_bubble.py      # 文字气泡：宠物左侧的即时文字反馈，支持双气泡堆叠
│   ├── chat_worker.py      # 后端逻辑：支持 Tool Calling 的异步 LLM 请求处理器
│   ├── settings_dialog.py  # 设置界面：侧边栏导航的高级配置中心
│   ├── tools.py            # 工具定义：供 LLM 调用的函数接口（感知器/执行器）
│   ├── styles.py           # 样式定义：统一的 QSS、颜色常量
│   └── __init__.py         # 模块包定义
├── config.json             # 运行时配置文件
└── requirements.txt        # 依赖列表
```

---

## 3. 主要组件详细说明

### 3.1 PetWidget (src/pet_widget.py)
**角色**：项目的“大脑”和“本体”。
- **自主意识 (Autonomous Brain)**：内置 `brain_timer`，每隔随机时间（30s-120s）触发一次 LLM 请求。
- **状态解析器**：能够解析模型返回的结构化数据 `[TEXT]...[/TEXT][STATE]...[/STATE]`，并自动执行 `set_action()` 变换宠物的动画状态。
- **交互入口**：
    - **双击**：强制触发一次 LLM 思考请求。
    - **右键**：提供“强制思考”、“切换动作”、“设置”等高级菜单。

### 3.2 Tools & ToolManager (src/tools.py)
**角色**：宠物的“感官”。
- 采用装饰器模式 `@tool_manager.register_tool` 注册工具。
- 提供环境检查（时间、日期）、模拟天气、用户活跃度等接口。
- LLM 在生成回复前会根据需要自主决定是否调用这些工具。

### 3.3 ChatBubble (src/chat_bubble.py)
**角色**：宠物的“嘴巴”。
- **定位更新**：气泡默认出现在宠物的 **左侧**。如果左侧空间不足，会自动智能漂移至右侧。
- **堆叠逻辑**：支持显示当前和上一条信息，提供上下文连贯性。

### 3.4 ChatWorker (src/chat_worker.py)
**角色**：异步网络处理器。
- **Tool Calling 支持**：实现了完整的“请求 -> 发现需求 -> 执行本地工具 -> 反馈结果 -> 最终回复”的迭代循环。
- 并发安全，确保主界面在模型思考时不会卡顿。

---

## 4. 通信与事件机制

项目主要采用 **信号与槽 (Signals & Slots)**：

| 信号/触发源 | 接收者 | 执行操作 |
| :--- | :--- | :--- |
| `PetWidget.brain_timer.timeout` | `PetWidget` | 执行 `send_brain_message()` 主动寻求 LLM 独白 |
| `PetWidget.mouseDoubleClickEvent`| `PetWidget` | 立即触发 `send_brain_message()` |
| `ChatWorker.response_received` | `PetWidget` | 解析响应标签，更新 `ChatBubble` 并切换 `PetState` |
| `SettingsDialog.settings_changed` | `PetWidget` | 实时热更新（速度、缩放、Prompt 等） |

---

## 5. 关键逻辑定位与修改指南

- **添加新工具**：在 `src/tools.py` 中编写函数并加上 `@tool_manager.register_tool` 装饰器，写好注释（LLM 会根据注释理解如何使用它）。
- **优化回复风格**：修改 `src/pet_widget.py` 中 `send_brain_message` 里的 `system_prompt`。
- **气泡样式**：在 `src/chat_bubble.py` 的 `SingleBubble` 类中调整 QSS。
- **动画添加**：在 `assets/actions/` 新建文件夹。若新状态需被 LLM 调用，确保其文件夹名称与模型预期的 `[STATE]` 值一致。

---

## 6. AI 辅助开发提示
1. **Tool Calling 逻辑**：修改 `ChatWorker` 时需注意 `max_iterations` 限制，防止模型死循环调用。
2. **状态容错**：在 `PetWidget` 解析 LLM 返回的 `[STATE]` 时，务必检查该状态是否存在于 `animation_frames` 中。
3. **坐标同步**：宠物移动或缩放后，需调用 `update_components_position()` 以同步左侧气泡位置。
