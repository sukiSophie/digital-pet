"""
聊天气泡组件模块
支持堆叠显示两个气泡（当前回复和上一次回复）
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt6.QtGui import QColor

from .styles import COLORS


class SingleBubble(QWidget):
    """单个聊天气泡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self.setup_ui()
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.start_fade_out)
        self.fade_animation = None
        
    def setup_ui(self):
        """设置 UI"""
        self.setObjectName("SingleBubble")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 气泡容器
        self.bubble_container = QWidget()
        self.bubble_container.setObjectName("BubbleContainer")
        self.bubble_container.setStyleSheet(f"""
            QWidget#BubbleContainer {{
                background-color: {COLORS['bubble_bg']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(139, 69, 19, 35))
        shadow.setOffset(0, 3)
        self.bubble_container.setGraphicsEffect(shadow)
        
        # 气泡内布局
        bubble_layout = QVBoxLayout(self.bubble_container)
        bubble_layout.setContentsMargins(14, 12, 14, 12)
        bubble_layout.setSpacing(0)
        
        # 文本标签
        self.text_label = QLabel()
        self.text_label.setObjectName("BubbleText")
        self.text_label.setWordWrap(True)
        # 固定宽度让它能够垂直增长
        self.text_label.setFixedWidth(280)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                background: transparent;
                line-height: 1.5;
            }}
        """)
        bubble_layout.addWidget(self.text_label)
        
        # 将容器放入主布局，并留出阴影所需的边距
        layout.setContentsMargins(10, 10, 10, 15)
        layout.addWidget(self.bubble_container)
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
        
    def show_message(self, text: str, duration: int = 5000):
        """显示消息"""
        self.text_label.setText(text)
        
        # 强制更新布局并计算大小
        self.bubble_container.adjustSize()
        self.adjustSize()
        
        # 对于窗口程序，显式设置大小
        self.setFixedSize(self.sizeHint())
        
        # 重置透明度
        self._opacity = 1.0
        self.setWindowOpacity(1.0)
        
        # 显示气泡
        self.show()
        
        # 设置自动隐藏
        if duration > 0:
            self.hide_timer.stop()
            self.hide_timer.start(duration)
    
    def start_fade_out(self):
        """开始淡出动画"""
        self.hide_timer.stop()
        
        if self.fade_animation:
            self.fade_animation.stop()
        
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(400)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
    
    def stop_timers(self):
        """停止所有计时器"""
        self.hide_timer.stop()
        if self.fade_animation:
            self.fade_animation.stop()


class ChatBubbleManager(QWidget):
    """聊天气泡管理器 - 支持堆叠两个气泡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 两个气泡：当前和上一个
        self.current_bubble = SingleBubble()
        self.current_bubble.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        self.previous_bubble = SingleBubble()
        self.previous_bubble.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # 上一个气泡使用稍微淡一点的样式
        self.previous_bubble.bubble_container.setStyleSheet(f"""
            QWidget#BubbleContainer {{
                background-color: rgba(255, 248, 243, 0.88);
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)
        self.previous_bubble.text_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_light']};
                font-size: 12px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                background: transparent;
                line-height: 1.3;
            }}
        """)
        
        self.pet_pos = QPoint(0, 0)
        self.pet_size = 100
        
    def show_message(self, text: str, duration: int = 5000):
        """显示新消息"""
        # 如果当前气泡有内容，移动到上一个
        if self.current_bubble.isVisible():
            current_text = self.current_bubble.text_label.text()
            if current_text:
                self.previous_bubble.stop_timers()
                self.previous_bubble.show_message(current_text, duration + 2000)
                self._update_positions()
        
        # 显示新消息
        self.current_bubble.stop_timers()
        self.current_bubble.show_message(text, duration)
        self._update_positions()
    
    def _update_positions(self):
        """更新气泡位置 - 出现在宠物左边"""
        # 计算当前气泡位置 (左侧)
        # 预留一些间距
        margin = 15
        current_x = self.pet_pos.x() - self.current_bubble.width() - margin
        current_y = self.pet_pos.y() + (self.pet_size // 4)  # 稍微偏上一点
        
        # 屏幕边界检查
        screen = self.current_bubble.screen()
        if screen:
            screen_geo = screen.geometry()
            
            # 如果左侧放不下，则尝试放在右侧
            if current_x < 10:
                current_x = self.pet_pos.x() + self.pet_size + margin
            
            # 确保不超出右边界
            if current_x + self.current_bubble.width() > screen_geo.width():
                current_x = screen_geo.width() - self.current_bubble.width() - 10
            
            # 垂直方向检查
            if current_y + self.current_bubble.height() > screen_geo.height():
                current_y = screen_geo.height() - self.current_bubble.height() - 10
            current_y = max(10, current_y)
        
        self.current_bubble.move(current_x, current_y)
        
        # 上一个气泡在当前气泡上方
        if self.previous_bubble.isVisible():
            prev_x = current_x
            prev_y = current_y - self.previous_bubble.height() - 8
            
            if screen:
                if prev_y < 10:
                     # 如果上方放不下，尝试放在下方？或者直接不显示？
                     # 这里简单处理，保持在上方但限制位置
                     prev_y = 10
            
            self.previous_bubble.move(prev_x, prev_y)

    
    def position_near_pet(self, pet_pos: QPoint, pet_size: int):
        """设置宠物位置并更新气泡位置"""
        self.pet_pos = pet_pos
        self.pet_size = pet_size
        self._update_positions()
    
    def close(self):
        """关闭所有气泡"""
        self.current_bubble.close()
        self.previous_bubble.close()
        super().close()


# 保持向后兼容
ChatBubble = ChatBubbleManager
