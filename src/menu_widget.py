"""
菜单组件模块
简化版菜单：只包含动作、聊天、设置三个按钮
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMenu, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QAction

from .styles import COLORS, ICON_BUTTON_STYLE


class MenuWidget(QWidget):
    """简化菜单组件 - 三个圆形按钮"""
    
    # 信号定义
    action_selected = pyqtSignal(str)   # 选择动作
    chat_requested = pyqtSignal()       # 打开聊天
    settings_requested = pyqtSignal()   # 打开设置
    close_requested = pyqtSignal()      # 关闭菜单
    
    def __init__(self, available_actions: list, expressions: list = None, parent=None):
        super().__init__(parent)
        self.available_actions = available_actions
        self.expressions = expressions or []
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        self.setObjectName("MenuWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主容器
        self.container = QWidget()
        self.container.setObjectName("MenuContainer")
        self.container.setStyleSheet(f"""
            QWidget#MenuContainer {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: 28px;
            }}
        """)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(139, 69, 19, 40))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(10)
        
        # 动作按钮
        self.action_btn = self._create_menu_button("🎭", "动作")
        self.action_btn.clicked.connect(self._show_action_menu)
        container_layout.addWidget(self.action_btn)
        
        # 聊天按钮
        self.chat_btn = self._create_menu_button("💬", "聊天")
        self.chat_btn.clicked.connect(self._on_chat_clicked)
        container_layout.addWidget(self.chat_btn)
        
        # 设置按钮
        self.settings_btn = self._create_menu_button("⚙️", "设置")
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        container_layout.addWidget(self.settings_btn)
        
        main_layout.addWidget(self.container)
        self.adjustSize()
        
    def _create_menu_button(self, icon: str, tooltip: str) -> QPushButton:
        """创建菜单按钮"""
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setFixedSize(46, 46)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text']};
                border: 2px solid transparent;
                border-radius: 23px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
                border-color: {COLORS['primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
            }}
        """)
        return btn
        
    def _show_action_menu(self):
        """显示动作子菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['background_solid']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 12px;
                padding: 8px 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 6px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['hover']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COLORS['border']};
                margin: 5px 10px;
            }}
        """)
        
        # 动作名称映射
        action_names = {
            'standby': '🧍 待机',
            'mention': '👋 打招呼',
            'eat': '🍖 吃东西',
            'sleep': '😴 睡觉',
            'love': '💕 喜欢',
            'left': '⬅️ 向左看',
            'right': '➡️ 向右看',
            'discomfort': '😣 不舒服'
        }
        
        # 重复型动作
        repeat_actions = ['standby', 'mention', 'sleep', 'left', 'right', 'discomfort']
        # 一次性动作
        once_actions = ['eat', 'love']
        
        # 添加重复型动作
        menu.addSection("🔁 持续动作")
        for action in self.available_actions:
            if action in repeat_actions:
                act = QAction(action_names.get(action, action), self)
                act.triggered.connect(lambda checked, a=action: self._on_action_selected(a))
                menu.addAction(act)
        
        menu.addSeparator()
        
        # 添加一次性动作
        menu.addSection("⚡ 一次性动作")
        for action in self.available_actions:
            if action in once_actions:
                act = QAction(action_names.get(action, action), self)
                act.triggered.connect(lambda checked, a=action: self._on_action_selected(a))
                menu.addAction(act)
        
        # 添加表情包
        if self.expressions:
            menu.addSeparator()
            menu.addSection("😊 表情包")
            for expr in self.expressions[:10]:  # 只显示前10个
                act = QAction(f"🎭 {expr}", self)
                act.triggered.connect(lambda checked, e=expr: self._on_action_selected(f"expr:{e}"))
                menu.addAction(act)
        
        # 在按钮下方显示菜单
        menu.exec(self.action_btn.mapToGlobal(QPoint(0, self.action_btn.height() + 5)))
    
    def _on_action_selected(self, action: str):
        """动作被选中"""
        self.action_selected.emit(action)
    
    def _on_chat_clicked(self):
        """聊天按钮点击"""
        self.chat_requested.emit()
    
    def _on_settings_clicked(self):
        """设置按钮点击"""
        self.settings_requested.emit()
    
    def position_near_pet(self, pet_pos: QPoint, pet_size: int):
        """定位到宠物附近（宠物上方）"""
        menu_x = pet_pos.x() + pet_size // 2 - self.width() // 2
        menu_y = pet_pos.y() - self.height() - 10
        
        screen = self.screen()
        if screen:
            screen_geo = screen.geometry()
            menu_x = max(10, min(menu_x, screen_geo.width() - self.width() - 10))
            menu_y = max(10, menu_y)
            
            # 如果上方空间不够，放到下方
            if menu_y < 10:
                menu_y = pet_pos.y() + pet_size + 10
        
        self.move(menu_x, menu_y)
    
    def update_actions(self, actions: list, expressions: list = None):
        """更新可用动作列表"""
        self.available_actions = actions
        if expressions:
            self.expressions = expressions
