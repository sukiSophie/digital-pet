"""
样式定义模块
使用半透明和暖色调主题，圆角设计
"""

# 暖色调配色方案
COLORS = {
    'primary': '#FF8B6A',          # 珊瑚橙
    'secondary': '#FFB799',         # 浅珊瑚
    'accent': '#FFCDB2',           # 米杏色
    'background': 'rgba(255, 245, 238, 0.92)',  # 半透明米白
    'background_solid': '#FFF5EE',  # 实色米白
    'text': '#5D4037',             # 咖啡棕
    'text_light': '#8D6E63',       # 浅咖啡
    'border': 'rgba(255, 139, 106, 0.3)',  # 半透明边框
    'shadow': 'rgba(139, 69, 19, 0.15)',   # 阴影
    'bubble_bg': 'rgba(255, 250, 245, 0.95)',  # 聊天气泡背景
    'input_bg': 'rgba(255, 255, 255, 0.85)',   # 输入框背景
    'hover': 'rgba(255, 139, 106, 0.2)',       # 悬停效果
}

# 菜单样式
MENU_STYLE = f"""
    QWidget#MenuWidget {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
    }}
"""

# 按钮样式
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
        min-height: 36px;
    }}
    QPushButton:hover {{
        background-color: #FF7A5C;
    }}
    QPushButton:pressed {{
        background-color: #E67259;
    }}
    QPushButton:disabled {{
        background-color: #D0D0D0;
        color: #888888;
    }}
"""

# 次要按钮样式
SECONDARY_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['accent']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 13px;
        min-height: 32px;
    }}
    QPushButton:hover {{
        background-color: #FFE0D0;
        border-color: {COLORS['primary']};
    }}
    QPushButton:pressed {{
        background-color: #FFD4C0;
    }}
"""

# 圆形图标按钮样式
ICON_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: white;
        border: none;
        border-radius: 20px;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        font-size: 16px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary']};
    }}
    QPushButton:pressed {{
        background-color: #E67259;
    }}
"""

# 输入框样式
INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {COLORS['input_bg']};
        border: 1.5px solid {COLORS['border']};
        border-radius: 12px;
        padding: 10px 15px;
        font-size: 14px;
        color: {COLORS['text']};
    }}
    QLineEdit:focus {{
        border-color: {COLORS['primary']};
        background-color: rgba(255, 255, 255, 0.95);
    }}
    QLineEdit::placeholder {{
        color: {COLORS['text_light']};
    }}
"""

# 文本编辑框样式
TEXT_EDIT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS['input_bg']};
        border: 1.5px solid {COLORS['border']};
        border-radius: 12px;
        padding: 10px;
        font-size: 14px;
        color: {COLORS['text']};
    }}
    QTextEdit:focus {{
        border-color: {COLORS['primary']};
        background-color: rgba(255, 255, 255, 0.95);
    }}
"""

# 标签样式
LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 14px;
        background: transparent;
    }}
"""

# 标题样式
TITLE_STYLE = f"""
    QLabel {{
        color: {COLORS['primary']};
        font-size: 16px;
        font-weight: bold;
        background: transparent;
    }}
"""

# 聊天气泡样式
CHAT_BUBBLE_STYLE = f"""
    QWidget#ChatBubble {{
        background-color: {COLORS['bubble_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
    }}
    QLabel#BubbleText {{
        color: {COLORS['text']};
        font-size: 14px;
        background: transparent;
        padding: 8px 12px;
    }}
"""

# 滚动区域样式
SCROLL_AREA_STYLE = f"""
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: {COLORS['accent']};
        width: 8px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['primary']};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #FF7A5C;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# 对话框样式
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLORS['background']};
        border-radius: 20px;
    }}
"""

# 组合框样式
COMBOBOX_STYLE = f"""
    QComboBox {{
        background-color: {COLORS['input_bg']};
        border: 1.5px solid {COLORS['border']};
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 14px;
        color: {COLORS['text']};
        min-height: 28px;
    }}
    QComboBox:hover {{
        border-color: {COLORS['primary']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS['text_light']};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['background_solid']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        selection-background-color: {COLORS['hover']};
        selection-color: {COLORS['text']};
        padding: 4px;
    }}
"""

# 滑块样式
SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        border: none;
        background: {COLORS['accent']};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['primary']};
        border: none;
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    QSlider::handle:horizontal:hover {{
        background: #FF7A5C;
    }}
    QSlider::sub-page:horizontal {{
        background: {COLORS['primary']};
        border-radius: 3px;
    }}
"""

# 分组框样式
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        background-color: rgba(255, 255, 255, 0.5);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 10px;
        font-size: 14px;
        color: {COLORS['text']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 15px;
        padding: 0 8px;
        background-color: {COLORS['background_solid']};
        color: {COLORS['primary']};
        font-weight: bold;
    }}
"""
# 侧边栏导航样式
SIDEBAR_STYLE = f"""
    QWidget#Sidebar {{
        background-color: rgba(255, 255, 255, 0.4);
        border-right: 1px solid {COLORS['border']};
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
    }}
"""

# 导航按钮样式
NAV_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text']};
        border: None;
        border-radius: 12px;
        padding: 12px 20px;
        font-size: 15px;
        text-align: left;
    }}
    QPushButton:hover {{
        background-color: {COLORS['hover']};
        color: {COLORS['primary']};
    }}
    QPushButton:checked {{
        background-color: {COLORS['primary']};
        color: white;
        font-weight: bold;
    }}
"""

# 标签页样式
TAB_STYLE = f"""
    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {COLORS['text_light']};
        padding: 10px 20px;
        margin-right: 5px;
        font-size: 14px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:hover {{
        color: {COLORS['primary']};
        background: {COLORS['hover']};
    }}
    QTabBar::tab:selected {{
        color: {COLORS['primary']};
        font-weight: bold;
        border-bottom: 2px solid {COLORS['primary']};
    }}
"""

# 上下文菜单样式
CONTEXT_MENU_STYLE = f"""
    QMenu {{
        background-color: rgba(255, 255, 255, 0.96);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 6px;
    }}
    QMenu::item {{
        background-color: transparent;
        padding: 8px 25px 8px 15px;
        margin: 2px 0px;
        border-radius: 8px;
        color: {COLORS['text']};
        font-size: 14px;
        font-weight: 500;
    }}
    QMenu::item:selected {{
        background-color: {COLORS['hover']};
        color: {COLORS['primary']};
        font-weight: bold;
    }}
    QMenu::separator {{
        height: 1px;
        background: {COLORS['border']};
        margin: 6px 12px;
    }}
    QMenu::icon {{
        position: absolute;
        left: 10px;
        top: 5px;
    }}
"""
