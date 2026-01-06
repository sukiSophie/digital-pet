
import inspect
import json
from typing import Callable, Dict, List, Any

class ToolManager:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._tool_descriptions: List[dict] = []

    def register_tool(self, func: Callable):
        """Decorator to register a tool."""
        # Get function signature and docstring
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or "No description provided."
        
        name = func.__name__
        
        # Simple schema generation
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            param_type = "string" # Default to string for simplicity
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == float:
                param_type = "number"
                
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}" 
            }
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": parameters
            }
        }
        
        self._tools[name] = func
        self._tool_descriptions.append(tool_def)
        return func

    def get_tool_definitions(self) -> List[dict]:
        return self._tool_descriptions

    def call_tool(self, name: str, args: dict) -> Any:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
        
        # 记录工具调用到日志
        print(f"[TOOL_CALL] 执行工具: {name} | 参数: {args}")
        
        try:
            return self._tools[name](**args)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

# Global instance for easy access
tool_manager = ToolManager()

# --- Example Tools ---

@tool_manager.register_tool
def get_current_state() -> str:
    """Get the current internal state of the pet (mood, health, etc)."""
    # This acts as a sensor
    return json.dumps({"hunger": 50, "mood": "neutral"})

@tool_manager.register_tool
def check_environment() -> str:
    """Check the desktop environment (time, etc)."""
    from datetime import datetime
    now = datetime.now()
    return json.dumps({
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "period": "morning" if 6 <= now.hour < 12 else "afternoon" if 12 <= now.hour < 18 else "evening"
    }, ensure_ascii=False)

@tool_manager.register_tool
def get_weather(city: str = "杭州") -> str:
    """Get the weather for a specific city."""
    # Mock weather data
    return json.dumps({
        "city": city,
        "weather": "晴朗",
        "temperature": "15°C",
        "humidity": "45%"
    }, ensure_ascii=False)

@tool_manager.register_tool
def get_system_health() -> str:
    """获取 Ubuntu 系统的实时资源状态，包括 CPU 使用率、温度和内存。"""
    try:
        import psutil
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        
        # 尝试通过 psutil 获取温度
        temps = {}
        if hasattr(psutil, "sensors_temperatures"):
            sensors = psutil.sensors_temperatures()
            for name, entries in sensors.items():
                if entries:
                    temps[name] = f"{entries[0].current}°C"
        
        return json.dumps({
            "cpu_usage": f"{cpu_usage}%",
            "memory_usage": f"{mem_usage}%",
            "temperatures": temps,
            "is_heavy_load": cpu_usage > 75
        }, ensure_ascii=False)
    except ImportError:
        return json.dumps({"error": "请安装 psutil 库以开启此功能"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@tool_manager.register_tool
def get_battery_status() -> str:
    """获取笔记本电量和充电状态。"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery is None:
            return json.dumps({"has_battery": False}, ensure_ascii=False)
        
        return json.dumps({
            "has_battery": True,
            "percent": f"{battery.percent}%",
            "power_plugged": battery.power_plugged,
            "is_low": battery.percent < 20
        }, ensure_ascii=False)
    except ImportError:
        return json.dumps({"error": "请安装 psutil 库"}, ensure_ascii=False)

@tool_manager.register_tool
def get_active_window_linux() -> str:
    """获取 Ubuntu 系统当前活动窗口的标题（需要 xorg 环境）。"""
    import subprocess
    try:
        # 获取活动窗口 ID
        out = subprocess.check_output(["xprop", "-root", "_NET_ACTIVE_WINDOW"], encoding='utf-8')
        window_id = out.split()[-1]
        if window_id == '0x0':
            return json.dumps({"window_title": "Desktop or None"}, ensure_ascii=False)
            
        # 获取窗口名称
        out = subprocess.check_output(["xprop", "-id", window_id, "WM_NAME", "_NET_WM_NAME"], encoding='utf-8')
        # 简单解析输出
        import re
        titles = re.findall(r'=\s*"(.*?)"', out)
        title = titles[0] if titles else "Unknown"
        
        return json.dumps({
            "active_window": title,
            "is_coding": any(app in title.lower() for app in ["vscode", "code", "terminal", "nvim", "pycharm", "cursor"]),
            "is_browsing": any(app in title.lower() for app in ["chrome", "firefox", "browser", "bilibili"])
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"window_title": "无法获取 (可能在 Wayland 下或缺失由 x11-utils 提供的 xprop)"}, ensure_ascii=False)


