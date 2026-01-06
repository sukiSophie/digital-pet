"""
聊天工作线程模块
使用 QThread 实现异步 API 调用
支持 OpenAI 兼容的多个 API 提供商
"""

import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal


from .tools import tool_manager

class ChatWorker(QThread):
    """聊天工作线程，异步处理 API 请求，并在必要时执行工具调用"""
    
    # 信号定义
    response_received = pyqtSignal(str)  # 成功接收响应
    error_occurred = pyqtSignal(str)      # 发生错误
    
    def __init__(self, api_key: str, endpoint: str, model_name: str,
                 system_prompt: str, user_message: str, tools: list = None, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.endpoint = endpoint
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_message = user_message
        self.tools = tools # List of tool definitions
    
    def run(self):
        """执行 API 请求，支持工具调用循环"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_message}
            ]
            
            # 限制工具调用循环次数，防止死循环
            max_iterations = 5
            
            for _ in range(max_iterations):
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 512
                }
                
                if self.tools:
                    payload["tools"] = self.tools
                    payload["tool_choice"] = "auto"

                response = requests.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    error_msg = f"API 错误: {response.status_code}"
                    try:
                        error_detail = response.json()
                        if 'error' in error_detail:
                            error_msg += f" - {error_detail['error'].get('message', '')}"
                    except:
                        pass
                    self.error_occurred.emit(error_msg)
                    return

                result = response.json()
                if 'choices' not in result or not result['choices']:
                    self.error_occurred.emit("响应格式错误")
                    return

                message = result['choices'][0]['message']
                
                # 检查是否有工具调用
                if 'tool_calls' in message and message['tool_calls']:
                    # 将助手的回复（包含 tool_calls）加入消息历史
                    messages.append(message)
                    
                    # 处理每个工具调用
                    for tool_call in message['tool_calls']:
                        function_name = tool_call['function']['name']
                        try:
                            args = json.loads(tool_call['function']['arguments'])
                        except:
                            args = {}
                        
                        # 执行工具
                        tool_result = tool_manager.call_tool(function_name, args)
                        
                        # 将工具执行结果加入消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call['id'],
                            "name": function_name,
                            "content": str(tool_result)
                        })
                    
                    # 继续循环，让 LLM 结合工具结果给出最终回复
                    continue
                else:
                    # 没有工具调用，直接返回内容
                    content = message.get('content', '')
                    self.response_received.emit(content)
                    return
            
            self.error_occurred.emit("达到最大工具调用次数限制")
                
        except requests.exceptions.Timeout:
            self.error_occurred.emit("请求超时，请稍后重试~")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("网络连接失败，请检查网络~")
        except Exception as e:
            self.error_occurred.emit(f"发生错误: {str(e)}")

