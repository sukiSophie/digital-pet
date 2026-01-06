# Digital-Pet 工具开发指南 (tools.md)

本文档旨在指导开发者如何为桌面宠物编写和注册新的工具函数（Tools）。通过工具，LLM 可以感知外部环境（如天气、系统状态）并采取行动。

---

## 1. 工具注册机制

项目使用 `src/tools.py` 中的 `ToolManager` 来管理所有工具。注册一个工具非常简单，只需使用装饰器模式。

### 核心步骤：
1. 在 `src/tools.py` 中定义一个 Python 函数。
2. 使用 `@tool_manager.register_tool` 装饰该函数。
3. **关键点**：务必编写清晰的 **Docstring** (文档字符串)，LLM 将根据这段文字来理解该工具的用途及何时调用它。

---

## 2. 编写规范

### 2.1 函数签名
- 尽量使用**类型注解**（Type Hints），这有助于系统生成更精确的 JSON Schema。
- 参数名应当具有描述性。

### 2.2 文档字符串 (Docstring)
- 第一行必须是该工具的功能简述。
- 如果有参数，建议在注释中说明参数的含义。

### 2.3 返回值
- 返回值必须是 **字符串 (str)**，建议使用 `json.dumps()` 封装复杂数据，并设置 `ensure_ascii=False` 以支持中文。

---

## 3. 代码示例

### 示例 1：无参数工具（感应器）
```python
@tool_manager.register_tool
def get_system_load() -> str:
    """获取系统当前的运行负载状态。当用户询问电脑累不累时调用。"""
    # 模拟获取逻辑
    import random
    load = random.choice(["低", "中", "高"])
    return json.dumps({"cpu_load": load, "status": "normal"}, ensure_ascii=False)
```

### 示例 2：带参数工具（执行器）
```python
@tool_manager.register_tool
def set_reminder(content: str, minutes_later: int) -> str:
    """
    为用户设置一个定时提醒。
    :param content: 提醒的具体内容
    :param minutes_later: 多少分钟后提醒
    """
    # 实际逻辑可以在此处实现（如启动 QTimer）
    return json.dumps({"result": "success", "msg": f"已设置 {minutes_later} 分钟后的提醒：{content}"}, ensure_ascii=False)
```

---

## 4. LLM 如何使用这些工具

1. **自动感知**：`PetWidget` 在启动 `ChatWorker` 时，会自动将所有已注册工具的定义（Name, Description, Parameters）发送给 LLM。
2. **决策循环**：
    - LLM 决定调用某个工具。
    - `ChatWorker` 在后台线程执行该函数。
    - `ChatWorker` 将函数结果反馈给 LLM。
    - LLM 根据结果生成最终的撒娇文本和动作建议。

---

## 5. 注意事项

1. **线程安全**：工具函数在 `ChatWorker` 的 `run()` 线程中执行。如果工具需要修改 UI 元素（如直接改变宠物大小），请务必使用 **信号 (Signal)** 机制发送到主线程处理，不要直接在工具函数内操作 UI。
2. **超时控制**：工具函数的执行时间不宜过长，否则会阻塞 API 的返回。
3. **错误处理**：建议在工具函数内部使用 `try...except`，并返回包含错误信息的 JSON 字符串，而不是直接抛出异常导致程序崩溃。
