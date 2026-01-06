"""
宠物窗口组件模块
实现图片轮播动画和交互功能
"""

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QMenu, QApplication,
    QSystemTrayIcon, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, pyqtSignal, QSize, QRect, QEvent
)
from PyQt6.QtGui import (
    QPixmap, QAction, QIcon, QCursor, QGuiApplication, QMouseEvent, QColor
)

from .chat_bubble import ChatBubble
from .chat_bubble import ChatBubble
# from .chat_window import ChatWindow # 已移除
from .settings_dialog import SettingsDialog
from .chat_worker import ChatWorker
from .styles import COLORS, CONTEXT_MENU_STYLE
from .tools import tool_manager

# 动作分类定义
REPEAT_ACTIONS = {'discomfort', 'left', 'right', 'mention', 'sleep', 'standby'}
ONCE_ACTIONS = {'eat', 'love'}  # 表情包也是一次性的，需动态判断



class PetWidget(QWidget):
    """宠物窗口组件"""
    
    def __init__(self, assets_path: str, config: dict, config_path: str, parent=None):
        super().__init__(parent)
        
        self.assets_path = assets_path
        self.config = config
        self.config_path = config_path
        
        # 动画相关
        self.current_action = "standby"
        self.previous_action = "standby"  # 记录上一个重复型动作
        self.is_one_time_action = False   # 标记当前是否为一次性动作
        self.current_scale = self.config.get('pet_scale', 0.5)
        self.scaled_animation_frames = {}
        self.animation_frames = {}
        self.current_frame_index = 0
        self.action_loop_count = 0        # 记录一次性动作的播放次数
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._next_frame)
        
        # 拖动相关
        self.dragging = False
        self.drag_offset = QPoint()
        
        # 子组件
        self.chat_bubble = None
        self.chat_window = None # 已移除，设为 None 防止 AttributeError
        self.chat_worker = None
        
        # 自主意识定时器
        self.brain_timer = QTimer(self)
        self.brain_timer.timeout.connect(self._on_brain_tick)
        self.brain_timer.setSingleShot(True) # 每次触发后重新计算随机时间
        
        # 初始化
        self.setup_ui()
        self.load_animations()
        self.setup_components()
        self.start_animation()
        self.start_brain()
        
        # 安装全局事件过滤器以处理菜单自动收起
        QApplication.instance().installEventFilter(self)
        
    def setup_ui(self):
        """设置 UI"""
        # 窗口设置：无边框、透明、始终置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 宠物图片标签
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_label.setScaledContents(False)
        
        # 添加阴影效果 (美化)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 60))  # 柔和的黑色阴影
        self.pet_label.setGraphicsEffect(shadow)
        
        # 初始位置（屏幕右下角）
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.geometry()
            self.move(screen_geo.width() - 250, screen_geo.height() - 300)
        
    def load_animations(self):
        """加载所有动画帧"""
        actions_path = os.path.join(self.assets_path, "actions")
        
        if not os.path.exists(actions_path):
            print(f"动作目录不存在: {actions_path}")
            return
        
        for action_name in os.listdir(actions_path):
            action_path = os.path.join(actions_path, action_name)
            if os.path.isdir(action_path):
                frames = []
                # 获取该动作的所有帧（按文件名排序）
                frame_files = sorted([
                    f for f in os.listdir(action_path)
                    if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))
                ])
                
                for frame_file in frame_files:
                    frame_path = os.path.join(action_path, frame_file)
                    pixmap = QPixmap(frame_path)
                    if not pixmap.isNull():
                        frames.append(pixmap)
                
                if frames:
                    self.animation_frames[action_name] = frames
                    print(f"加载动作 '{action_name}': {len(frames)} 帧")
        for action_name in os.listdir(actions_path):
            action_path = os.path.join(actions_path, action_name)
            if os.path.isdir(action_path):
                frames = []
                # 获取该动作的所有帧（按文件名排序）
                frame_files = sorted([
                    f for f in os.listdir(action_path)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                ])
                
                for frame_file in frame_files:
                    frame_path = os.path.join(action_path, frame_file)
                    pixmap = QPixmap(frame_path)
                    if not pixmap.isNull():
                        frames.append(pixmap)
                
                if frames:
                    self.animation_frames[action_name] = frames
                    print(f"加载动作 '{action_name}': {len(frames)} 帧")
        
        # 加载表情包 (expressions) 到 animation_frames，前缀 'expr:'
        expr_path = os.path.join(self.assets_path, "expressions")
        if os.path.exists(expr_path):
            for expr_file in os.listdir(expr_path):
                if expr_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # 表情包通常是单帧，但为了统一处理，作为单帧动画
                    pixmap = QPixmap(os.path.join(expr_path, expr_file))
                    if not pixmap.isNull():
                        # 去掉扩展名作为动作名
                        action_name = f"expr:{os.path.splitext(expr_file)[0]}"
                        self.animation_frames[action_name] = [pixmap]
                        ONCE_ACTIONS.add(action_name) # 标记为一次性
                        print(f"加载表情 '{action_name}'")

        if "standby" not in self.animation_frames:
            # 如果没有 standby 动作，使用第一个可用的动作
            if self.animation_frames:
                first_action = list(self.animation_frames.keys())[0]
                self.animation_frames["standby"] = self.animation_frames[first_action]
        
        # 预先生成缩放缓存 (性能优化)
        self._update_scaled_frames()

    def _update_scaled_frames(self):
        """更新缩放后的动画帧缓存"""
        self.scaled_animation_frames.clear()
        
        if not self.animation_frames:
            return
            
        print(f"正在预处理缩放动画帧 (Scale: {self.current_scale})...")
        
        for action, frames in self.animation_frames.items():
            scaled_list = []
            for pixmap in frames:
                if pixmap.isNull():
                    continue
                    
                new_size = QSize(
                    int(pixmap.width() * self.current_scale),
                    int(pixmap.height() * self.current_scale)
                )
                
                scaled_pixmap = pixmap.scaled(
                    new_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled_list.append(scaled_pixmap)
            
            self.scaled_animation_frames[action] = scaled_list
        
    def setup_components(self):
        """设置子组件"""
        # 创建聊天气泡
        self.chat_bubble = ChatBubble()
        
        # 获取可用动作列表
        available_actions = list(self.animation_frames.keys())
        if not available_actions:
            available_actions = ["standby"]
        
        # 创建动作菜单 (已移除冗余的 MenuWidget)
        # available_actions = list(self.animation_frames.keys())
        # ...
        
    def start_animation(self):
        """开始播放动画"""
        interval = self.config.get('animation_interval', 150)
        self.animation_timer.start(interval)
        self._show_current_frame()
        
    def _next_frame(self):
        """切换到下一帧"""
        # 处理移动逻辑
        self._handle_movement()
        
        frames = self.animation_frames.get(self.current_action, [])
        if not frames:
            return
            
        next_index = self.current_frame_index + 1
        
        # 检查是否播放结束
        if next_index >= len(frames):
            if self.is_one_time_action:
                self.action_loop_count += 1
                if self.action_loop_count >= 2:
                    # 一次性动作播放结束（已完成2次），恢复之前的动作
                    self.set_action(self.previous_action)
                    return
                else:
                    # 开始第二次循环
                    next_index = 0
            else:
                # 重复性动作，循环播放
                next_index = 0
                
        self.current_frame_index = next_index
        self._show_current_frame()
    
    def _handle_movement(self):
        """处理行走移动逻辑"""
        step = 20  # 每次移动像素
        
        if self.current_action == 'left':
            new_pos = self.x() - step
            if new_pos < 100:
                # 碰到左边界，转身向右
                self.set_action('right')
            else:
                self.move(new_pos, self.y())
                
        elif self.current_action == 'right':
            screen = self.screen()
            if screen:
                screen_width = screen.geometry().width()
                new_pos = self.x() + step
                if new_pos + self.width() > screen_width:
                    # 碰到右边界，转身向左
                    self.set_action('left')
                else:
                    self.move(new_pos, self.y())
                    
    def moveEvent(self, event):
        """窗口移动事件"""
        self.update_components_position()
        super().moveEvent(event)
        
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        self.update_components_position()
        super().resizeEvent(event)

    def update_components_position(self):
        """更新所有附加组件的位置"""
        # 更新气泡位置
        if self.chat_bubble:
            self.chat_bubble.position_near_pet(self.pos(), self.width())
            
        # 更新菜单位置
            
        # 更新位置逻辑已在上方由 chat_bubble 处理
    
    def _show_current_frame(self):
        """显示当前帧"""
        # 使用缓存的缩放帧 (性能优化)
        frames = self.scaled_animation_frames.get(self.current_action, [])
        if frames and 0 <= self.current_frame_index < len(frames):
            pixmap = frames[self.current_frame_index]
            self.pet_label.setPixmap(pixmap)
            self.pet_label.adjustSize()
            self.setFixedSize(self.pet_label.size())
    
    def set_action(self, action: str):
        """设置当前动作"""
        if action not in self.animation_frames:
            return
            
        # 判断动作类型
        is_once = action in ONCE_ACTIONS or action.startswith('expr:') or action not in REPEAT_ACTIONS
        
        # 如果是 mention 且正在进行中，不重复设置
        if action == 'mention' and self.current_action == 'mention':
            return

        if is_once:
            # 如果是一次性动作，记录当前状态（如果当前不是一次性动作）
            if not self.is_one_time_action:
                self.previous_action = self.current_action
            self.is_one_time_action = True
        else:
            # 如果是重复动作，更新 previous_action 为这个新动作（除非它是临时的 mention）
            if action != 'mention':
                self.previous_action = action
            self.is_one_time_action = False
            
        self.current_action = action
        self.current_frame_index = 0
        self.action_loop_count = 0  # 重置播放次数
        self._show_current_frame()
        
        # 更新菜单中的当前动作（仅当是重复动作时，或者是正在展示的菜单需要更新状态时）
        # if self.menu_widget and not is_once:
        #     self.menu_widget.set_current_action(action)
    
    def send_chat_message(self, message: str):
        """发送聊天消息"""
        # 获取当前 Provider 设置
        provider = self.config.get('api_provider', 'zhipu')
        provider_settings = self.config.get('api_settings', {}).get(provider, {})
        
        start_api_key = provider_settings.get('api_key', '')
        if not start_api_key:
             # 尝试从根目录获取（兼容旧配置）
             start_api_key = self.config.get('api_key', '')

        if not start_api_key or start_api_key == 'YOUR_API_KEY_HERE':
            self._show_bubble("请先在设置中配置 API Key 哦~")
            return
        
        # 显示思考中 (仅当聊天窗口不可见时显示气泡)
        # 始终显示气泡，因为聊天窗口已移除
        self._show_bubble("让我想想...")
        
        # 获取默认配置
        default_endpoints = {
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
            'deepseek': 'https://api.deepseek.com/chat/completions',
            'model_scope': 'https://api-inference.modelscope.cn/v1/chat/completions' # 示例，需确认
        }
        
        default_models = {
            'zhipu': 'glm-4-flash',
            'deepseek': 'deepseek-chat',
            'model_scope': 'qwen-turbo'
        }
        
        endpoint = provider_settings.get('base_url', '')
        if not endpoint:
            endpoint = default_endpoints.get(provider, '')
        else:
            # 如果配置了 base_url，智能补全 path
            endpoint = endpoint.strip('/')
            if not endpoint.endswith('chat/completions'):
                endpoint = f"{endpoint}/chat/completions"

        model = provider_settings.get('model_name', '') or default_models.get(provider, 'glm-4-flash')
        system_prompt = self.config.get('system_prompt', '你是一个可爱的桌面宠物助手')

        # 创建工作线程
        self.chat_worker = ChatWorker(
            api_key=start_api_key,
            endpoint=endpoint,
            model_name=model,
            system_prompt=system_prompt,
            user_message=message
        )
        
        self.chat_worker.response_received.connect(self._on_chat_response)
        self.chat_worker.error_occurred.connect(self._on_chat_error)
        self.chat_worker.start()
        
        # 显示在聊天窗口
        # 聊天窗口已移除
        # if self.chat_window:
        #     self.chat_window.add_thinking_indicator()

    def on_user_chat_message(self, message: str):
        """处理用户从窗口输入的聊天消息"""
        self.send_chat_message(message)
    
    def _on_chat_response(self, response: str):
        """处理聊天响应"""
        print(f"Raw Brain Response: {response}")
        # 解析响应：可能包含 [TEXT] 和 [STATE]
        text_content = ""
        state_content = ""
        
        import re
        # 更加鲁棒的正则：TEXT 匹配会在 [/TEXT] 或 [STATE] 之前停止，防止吞噬后面动作标签
        text_match = re.search(r"\[TEXT\]\s*(.*?)(?=\s*\[/TEXT\]|\s*\[STATE\]|$)", response, re.DOTALL | re.IGNORECASE)
        state_match = re.search(r"\[STATE\]\s*(.*?)(?=\s*\[/STATE\]|$)", response, re.DOTALL | re.IGNORECASE)
        
        if text_match:
            text_content = text_match.group(1).strip()
        else:
            # 备选：如果完全没有 [TEXT] 标签，则尝试清洗掉 [STATE] 标签后作为文本
            text_content = re.sub(r"\[STATE\].*?(?:\[/STATE\]|$)", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
            
        if state_match:
            state_content = state_match.group(1).strip().lower()
            # 清理可能残留的标签
            state_content = re.sub(r"\[/?(TEXT|STATE)\]", "", state_content, flags=re.IGNORECASE).strip()

        # 最终保险：强行抹除 text_content 中可能残留的任何标签字符，确保用户看不到 [TEXT] 或 [STATE]
        text_content = re.sub(r"\[/?(TEXT|STATE)\]", "", text_content, flags=re.IGNORECASE).strip()


        # 显示文本气泡
        if text_content:
            self._show_bubble(text_content, duration=8000)
            
        # 切换状态
        if state_content:
            # 尝试模糊匹配或直接匹配
            target_state = None
            # 清理可能的标点符号（如 eat. -> eat）
            state_content = re.sub(r'[^\w\s]', '', state_content).strip()
            
            if state_content in self.animation_frames:
                target_state = state_content
            # 映射表：处理模型常见的表达偏差
            mappings = {
                "discomfortable": "discomfort",
                "sad": "discomfort",
                "hungry": "eat",
                "eating": "eat",
                "sleeping": "sleep",
                "tired": "sleep",
                "walking": "left", # 默认走路选左
                "moving": "right"
            }
            
            if not target_state and state_content in mappings:
                mapped = mappings[state_content]
                if mapped in self.animation_frames:
                    target_state = mapped
            
            if target_state:
                if target_state == "mention":
                    print("LLM 试图调用受限动作 'mention'，已拦截。")
                    target_state = None
            
            if target_state:
                print(f"LLM 请求切换状态: {target_state}")
                self.set_action(target_state)
            else:
                print(f"LLM 请求了不可用的状态: {state_content}")
        
        # 安排下一次“思考”
        self.start_brain()
    
    def _on_chat_error(self, error: str):
        """处理聊天错误"""
        print(f"Brain Error: {error}")
        # 安排下一次“思考”
        self.start_brain()
        
    def start_brain(self):
        """启动/安排下一次自主思考"""
        import random
        # 随机时间：120秒到480秒之间
        interval = random.randint(120000, 480000)
        self.brain_timer.start(interval)
        print(f"下一次自主思考将在 {interval/1000} 秒后发生")

    def _on_brain_tick(self):
        """自主思考触发"""
        self.send_brain_message()

    def send_brain_message(self):
        """向 LLM 发送自主思考请求"""
        # 获取当前 Provider 设置
        provider = self.config.get('api_provider', 'zhipu')
        provider_settings = self.config.get('api_settings', {}).get(provider, {})
        
        start_api_key = provider_settings.get('api_key', '')
        if not start_api_key:
             start_api_key = self.config.get('api_key', '')

        if not start_api_key or start_api_key == 'YOUR_API_KEY_HERE':
            return
        
        # 获取默认配置
        default_endpoints = {
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
            'deepseek': 'https://api.deepseek.com/chat/completions',
            'model_scope': 'https://api-inference.modelscope.cn/v1/chat/completions'
        }
        
        default_models = {
            'zhipu': 'glm-4-flash',
            'deepseek': 'deepseek-chat',
            'model_scope': 'qwen-turbo'
        }
        
        endpoint = provider_settings.get('base_url', '')
        if not endpoint:
            endpoint = default_endpoints.get(provider, '')
        else:
            endpoint = endpoint.strip('/')
            if not endpoint.endswith('chat/completions'):
                endpoint = f"{endpoint}/chat/completions"

        model = provider_settings.get('model_name', '') or default_models.get(provider, 'glm-4-flash')
        
        # 构建增强型 System Prompt
        base_prompt = self.config.get('system_prompt', '你是一个可爱的桌面宠物助手')
        # 过滤掉 mention 动作，模型不允许主动触发它
        allowed_states = [s for s in self.animation_frames.keys() if s != 'mention']
        available_states = ", ".join(allowed_states)
        
        system_prompt = f"""
{base_prompt}

你需要结合工具返回的信息（如时间、宠物状态等）向用户撒欢或撒娇。
你的回复必须**严格遵循**以下格式，不要有任何开场白：
""
[TEXT] 这里是你对用户说的话，要可爱、调皮、像在撒娇一样 [/TEXT]
[STATE] 这里是你想要切换到的动作状态，必须从以下列表中选择一个：{available_states} [/STATE]
""
注意：
1. 你的话语要短小精悍，通常在 20 字以内。
2. 你可以随时调用工具来了解外部世界。
"""

        # 创建工作线程
        self.chat_worker = ChatWorker(
            api_key=start_api_key,
            endpoint=endpoint,
            model_name=model,
            system_prompt=system_prompt,
            user_message="请根据当前情况自主产生一段独白或行为。",
            tools=tool_manager.get_tool_definitions()
        )
        
        self.chat_worker.response_received.connect(self._on_chat_response)
        self.chat_worker.error_occurred.connect(self._on_chat_error)
        self.chat_worker.start()
    
    def _show_bubble(self, text: str, duration: int = 5000):
        """显示聊天气泡"""
        if self.chat_bubble:
            # 先更新位置，确保在正确位置显示
            self.update_components_position()
            self.chat_bubble.show_message(text, duration)
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self.config_path, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
    
    def _on_settings_changed(self, new_config: dict):
        """处理设置变更"""
        old_scale = self.current_scale
        self.config = new_config
        
        # 更新动画速度
        interval = self.config.get('animation_interval', 150)
        self.animation_timer.setInterval(interval)
        
        # 更新缩放
        new_scale = self.config.get('pet_scale', 0.5)
        if abs(new_scale - old_scale) > 0.001: 
            self.current_scale = new_scale
            self._update_scaled_frames()
            
        self._show_current_frame()
        
        self._show_bubble("设置已保存~")
    
    # toggle_menu 方法已移除

    def toggle_chat_window(self):
        """切换聊天窗口 (已弃用)"""
        pass
    
    # ===== 鼠标事件 =====
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.position().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            
            # 触发 mention 动作
            if 'mention' in self.animation_frames:
                self.set_action('mention')
                
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
            
            # 位置更新由 moveEvent 自动处理
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            # 恢复动作 (如果当前是 mention)
            if self.current_action == 'mention':
                # 回到之前的重复性动作
                self.set_action(self.previous_action)
                
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击 - 已禁用"""
        pass
    
    def enterEvent(self, event):
        """鼠标进入"""
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
    
    def leaveEvent(self, event):
        """鼠标离开"""
        if not self.dragging:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单"""
        menu = QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setStyleSheet(CONTEXT_MENU_STYLE)
        
        # 菜单项 (移除打开对话)
        # chat_action = QAction("💬 打开对话", self)
        # chat_action.triggered.connect(self.toggle_chat_window)
        # menu.addAction(chat_action)
        
        think_action = QAction("💭 强制思考", self)
        think_action.triggered.connect(self.send_brain_message)
        menu.addAction(think_action)
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 动作子菜单
        actions_menu = menu.addMenu("🎭 切换动作")
        actions_menu.setWindowFlags(actions_menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        actions_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        for action_name in self.animation_frames.keys():
            action = QAction(action_name, self)
            action.triggered.connect(lambda checked, a=action_name: self.set_action(a))
            actions_menu.addAction(action)
        
        menu.addSeparator()
        
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec(pos)
    
    def eventFilter(self, obj, event):
        """全局事件过滤器"""
        return super().eventFilter(obj, event)

    def _check_menu_autoclose(self):
        """检查是否需要自动关闭菜单 (已弃用)"""
        pass

    def closeEvent(self, event):
        """关闭事件"""
        # 移除事件过滤器
        QApplication.instance().removeEventFilter(self)
        
        if self.chat_bubble:
            self.chat_bubble.close()
        
        event.accept()
