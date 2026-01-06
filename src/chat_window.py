"""
聊天窗口组件模块
独立的聊天对话窗口
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor

from .styles import (
    COLORS, BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    INPUT_STYLE, ICON_BUTTON_STYLE, SCROLL_AREA_STYLE
)


class ChatMessage(QWidget):
    """单条聊天消息"""
    
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user_msg = is_user
        self.setup_ui(text, is_user)
        
    def setup_ui(self, text: str, is_user: bool):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 消息气泡
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(240)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            # 用户在左侧
            bubble.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border-radius: 14px;
                    border-bottom-left-radius: 4px;
                    padding: 10px 14px;
                    font-size: 14px;
                    line-height: 1.4;
                }}
            """)
            layout.addWidget(bubble)
            layout.addStretch()
        else:
            # 宠物在右侧
            layout.addStretch()
            bubble.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS['accent']};
                    color: {COLORS['text']};
                    border-radius: 14px;
                    border-bottom-right-radius: 4px;
                    padding: 10px 14px;
                    font-size: 14px;
                    line-height: 1.4;
                }}
            """)
            layout.addWidget(bubble)


class ChatWindow(QWidget):
    """聊天窗口"""
    
    # 信号
    message_sent = pyqtSignal(str)
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        self.setObjectName("ChatWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setFixedSize(340, 420)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主容器 - 透明化
        self.container = QWidget()
        self.container.setObjectName("ChatContainer")
        self.container.setStyleSheet(f"""
            QWidget#ChatContainer {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # 移除阴影效果 (因为整体透明了)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(5, 5, 5, 5) # 减少边距
        container_layout.setSpacing(5)
        
        # 移除标题栏和分隔线，直接显示消息区域
        
        # 消息区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['primary']};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_widget)
        container_layout.addWidget(self.scroll_area, 1)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        # 稍微调整输入框样式，使其看起来更像悬浮的
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 1.5px solid {COLORS['border']};
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                background-color: rgba(255, 255, 255, 0.98);
            }}
        """)
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("📤")
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet(ICON_BUTTON_STYLE)
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)
        
        container_layout.addLayout(input_layout)
        
        main_layout.addWidget(self.container)
        
    
    def _send_message(self):
        """发送消息"""
        text = self.input_field.text().strip()
        if text:
            self.add_message(text, is_user=True)
            self.message_sent.emit(text)
            self.input_field.clear()
    
    def add_message(self, text: str, is_user: bool = False):
        """添加消息 (各显示两条)"""
        # 1. 统计当前各类消息
        user_msgs = []
        pet_msgs = []
        
        for i in range(self.messages_layout.count()):
            item = self.messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatMessage):
                w = item.widget()
                if w.is_user_msg:
                    user_msgs.append((i, w))
                else:
                    pet_msgs.append((i, w))
        
        # 2. 分别限制数量
        if is_user:
            if len(user_msgs) >= 2:
                idx, w = user_msgs[0]
                w.deleteLater()
                self.messages_layout.takeAt(idx)
        else:
            if len(pet_msgs) >= 2:
                idx, w = pet_msgs[0]
                w.deleteLater()
                self.messages_layout.takeAt(idx)

        # 3. 移除最后的弹簧
        for i in range(self.messages_layout.count() - 1, -1, -1):
            item = self.messages_layout.itemAt(i)
            if item and not item.widget():
                self.messages_layout.takeAt(i)
                break
        
        # 4. 添加新消息
        msg = ChatMessage(text, is_user)
        self.messages_layout.addWidget(msg)
        
        # 5. 重新添加弹簧并滚动
        self.messages_layout.addStretch()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def add_thinking_indicator(self):
        """添加思考中指示"""
        self.add_message("思考中...", is_user=False)
    
    def remove_last_message(self):
        """移除最后一条消息（用于替换思考指示器）"""
        # 找到最后一条消息（由于弹簧在最后，所以反向查找第一条 widget）
        for i in range(self.messages_layout.count() - 1, -1, -1):
            item = self.messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatMessage):
                widget = item.widget()
                widget.deleteLater()
                self.messages_layout.takeAt(i)
                break
    
    def _clear_messages(self):
        """清空消息"""
        while self.messages_layout.count() > 0:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.messages_layout.addStretch()
    
    def _on_close(self):
        """关闭窗口"""
        self.close_requested.emit()
        self.hide()
    
    def position_near_pet(self, pet_pos: QPoint, pet_size: int):
        """定位到宠物附近 (优先左侧)"""
        # 默认在左侧
        chat_x = pet_pos.x() - self.width() - 15
        chat_y = pet_pos.y() - 50
        
        screen = self.screen()
        if screen:
            screen_geo = screen.geometry()
            
            # 如果左侧空间不够，放右侧
            if chat_x < 10:
                chat_x = pet_pos.x() + pet_size + 15
                
                # 如果右侧也不够（虽然不太可能），保持在屏幕内
                if chat_x + self.width() > screen_geo.width():
                     chat_x = screen_geo.width() - self.width() - 10
                     
            chat_y = max(10, min(chat_y, screen_geo.height() - self.height() - 10))
        
        self.move(chat_x, chat_y)
    
    # 拖动窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
