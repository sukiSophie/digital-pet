import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QSlider, QComboBox, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QTextEdit,
    QStackedWidget, QWidget, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

from .styles import (
    COLORS, BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    INPUT_STYLE, LABEL_STYLE, TITLE_STYLE,
    COMBOBOX_STYLE, SLIDER_STYLE, GROUP_BOX_STYLE, 
    TEXT_EDIT_STYLE, SIDEBAR_STYLE, NAV_BUTTON_STYLE
)


class SettingsDialog(QDialog):
    """设置对话框 - 重构后的 Premium 版本"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config: dict, config_path: str, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.config_path = config_path
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置高级 UI 布局"""
        self.setWindowTitle("设置 ⚙️")
        self.setFixedSize(680, 520) # 调宽一点，适应侧边栏
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        
        # 主外层布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 主容器
        self.container = QWidget()
        self.container.setObjectName("SettingsContainer")
        self.container.setStyleSheet(f"""
            QWidget#SettingsContainer {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
            }}
        """)
        
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # --- 左侧侧边栏 ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 30, 10, 20)
        sidebar_layout.setSpacing(8)
        
        # 侧边栏标题
        sidebar_title = QLabel("Menu")
        sidebar_title.setStyleSheet(f"color: {COLORS['text_light']}; font-weight: bold; margin-bottom: 10px; margin-left: 10px;")
        sidebar_layout.addWidget(sidebar_title)
        
        # 导航按钮组
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        self.btn_api = self._create_nav_btn("🔑  API 设置", 0)
        self.btn_pet = self._create_nav_btn("🐾  宠物设置", 1)
        self.btn_about = self._create_nav_btn("ℹ️  关于项目", 2)
        
        sidebar_layout.addWidget(self.btn_api)
        sidebar_layout.addWidget(self.btn_pet)
        sidebar_layout.addWidget(self.btn_about)
        sidebar_layout.addStretch()
        
        # 底部 Logo 或版本号
        ver_label = QLabel("v1.2.0")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 11px;")
        sidebar_layout.addWidget(ver_label)
        
        container_layout.addWidget(self.sidebar)
        
        # --- 右侧内容区 ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(15)
        
        # 顶部标题区域
        header_layout = QHBoxLayout()
        self.page_title = QLabel("API 设置")
        self.page_title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['primary']};")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_light']};
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                color: {COLORS['primary']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        content_layout.addLayout(header_layout)
        
        # 页面容器 (Stacked Widget)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_api_page())
        self.stack.addWidget(self._create_pet_page())
        self.stack.addWidget(self._create_about_page())
        content_layout.addWidget(self.stack)
        
        # 底部操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存修改")
        save_btn.setStyleSheet(BUTTON_STYLE)
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self.save_settings)
        bottom_layout.addWidget(save_btn)
        content_layout.addLayout(bottom_layout)
        
        container_layout.addWidget(content_area, 1)
        main_layout.addWidget(self.container)
        
        # 默认选中第一页
        self.btn_api.setChecked(True)

    def _create_nav_btn(self, text: str, index: int) -> QPushButton:
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet(NAV_BUTTON_STYLE)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.nav_group.addButton(btn, index)
        btn.clicked.connect(lambda: self._on_nav_clicked(index, text))
        return btn

    def _on_nav_clicked(self, index: int, text: str):
        """处理导航点击"""
        self.stack.setCurrentIndex(index)
        # 移除图标部分后的文字作为标题
        title = text.strip().split('  ')[-1]
        self.page_title.setText(title)

    def _create_api_page(self) -> QWidget:
        """主 API 设置页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 提供商选择栏
        provider_bar = QHBoxLayout()
        provider_bar.addWidget(self._create_label("模型供应商："))
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["智谱 AI", "DeepSeek", "ModelScope"])
        self.provider_combo.setStyleSheet(COMBOBOX_STYLE)
        self.provider_combo.setFixedWidth(160)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_bar.addWidget(self.provider_combo)
        provider_bar.addStretch()
        layout.addLayout(provider_bar)
        
        # 这里使用一个内部 StackedWidget 来切换不同的 Provider 设置界面
        self.api_stack = QStackedWidget()
        self.zhipu_group = self._create_provider_form("智谱 AI (Zhipu)", "zhipu")
        self.deepseek_group = self._create_provider_form("DeepSeek API", "deepseek")
        self.modelscope_group = self._create_provider_form("ModelScope", "model_scope")
        
        self.api_stack.addWidget(self.zhipu_group)
        self.api_stack.addWidget(self.deepseek_group)
        self.api_stack.addWidget(self.modelscope_group)
        
        layout.addWidget(self.api_stack)
        layout.addStretch()
        return page

    def _create_provider_form(self, title: str, key: str) -> QWidget:
        """创建单个 Provider 的表单"""
        group = QGroupBox(title)
        group.setStyleSheet(GROUP_BOX_STYLE)
        layout = QFormLayout(group)
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setSpacing(15)
        
        api_key = QLineEdit()
        api_key.setPlaceholderText("API Key (sk-...)")
        api_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_key.setStyleSheet(INPUT_STYLE)
        setattr(self, f"{key}_api_key", api_key)
        layout.addRow(self._create_label("API Key:"), api_key)
        
        base_url = QLineEdit()
        base_url.setPlaceholderText("API 请求基础 URL")
        base_url.setStyleSheet(INPUT_STYLE)
        setattr(self, f"{key}_base_url", base_url)
        layout.addRow(self._create_label("基础地址:"), base_url)
        
        model_name = QLineEdit()
        model_name.setPlaceholderText("例如: glm-4, deepseek-chat")
        model_name.setStyleSheet(INPUT_STYLE)
        setattr(self, f"{key}_model_name", model_name)
        layout.addRow(self._create_label("模型名称:"), model_name)
        
        return group

    def _create_pet_page(self) -> QWidget:
        """主宠物设置页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 性格设定
        prompt_group = QGroupBox("个性化设定")
        prompt_group.setStyleSheet(GROUP_BOX_STYLE)
        prompt_layout = QVBoxLayout(prompt_group)
        prompt_layout.setContentsMargins(15, 20, 15, 15)
        
        prompt_header = QLabel("系统提示词 (System Prompt):")
        prompt_header.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 13px; font-weight: bold;")
        prompt_layout.addWidget(prompt_header)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("在这里定义宠物的性格、语言风格和特殊癖好...")
        self.prompt_input.setStyleSheet(TEXT_EDIT_STYLE)
        self.prompt_input.setFixedHeight(120)
        prompt_layout.addWidget(self.prompt_input)
        layout.addWidget(prompt_group)
        
        # 显示动态控制
        display_group = QGroupBox("显示与交互")
        display_group.setStyleSheet(GROUP_BOX_STYLE)
        display_layout = QFormLayout(display_group)
        display_layout.setContentsMargins(15, 25, 15, 15)
        display_layout.setSpacing(15)
        
        # 动画速度
        speed_box = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setStyleSheet(SLIDER_STYLE)
        self.speed_slider.valueChanged.connect(self._update_speed_label)
        speed_box.addWidget(self.speed_slider)
        self.speed_label = QLabel("150ms")
        self.speed_label.setFixedWidth(50)
        self.speed_label.setStyleSheet("color: " + COLORS['primary'] + "; font-weight: bold;")
        speed_box.addWidget(self.speed_label)
        display_layout.addRow(self._create_label("动画帧间隔:"), speed_box)
        
        # 缩放比例
        scale_box = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(20, 150)
        self.scale_slider.setStyleSheet(SLIDER_STYLE)
        self.scale_slider.valueChanged.connect(self._update_scale_label)
        scale_box.addWidget(self.scale_slider)
        self.scale_label = QLabel("50%")
        self.scale_label.setFixedWidth(50)
        self.scale_label.setStyleSheet("color: " + COLORS['primary'] + "; font-weight: bold;")
        scale_box.addWidget(self.scale_label)
        display_layout.addRow(self._create_label("宠物缩放比例:"), scale_box)
        
        layout.addWidget(display_group)
        layout.addStretch()
        return page

    def _create_about_page(self) -> QWidget:
        """关于页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # 图标
        icon_label = QLabel("🎨")
        icon_label.setStyleSheet("font-size: 60px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        app_name = QLabel("Digital Pet Pro")
        app_name.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['text']};")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name)
        
        desc = QLabel("一个基于 PyQt6 和大型语言模型的\n桌面互动宠物项目。")
        desc.setStyleSheet(f"color: {COLORS['text_light']}; line-height: 1.5;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        github_btn = QPushButton("访问 GitHub 项目主页")
        github_btn.setFixedWidth(200)
        github_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(github_btn)
        
        layout.addStretch()
        return page

    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(LABEL_STYLE)
        return label
    
    def _update_speed_label(self, value: int):
        self.speed_label.setText(f"{value}ms")
        
    def _update_scale_label(self, value: int):
        self.scale_label.setText(f"{value}%")
    
    def _on_provider_changed(self, index: int):
        """同步切换 API 界面"""
        self.api_stack.setCurrentIndex(index)
        
    def load_settings(self):
        """从配置字典加载数据到 UI"""
        provider = self.config.get('api_provider', 'zhipu')
        provider_map = {'zhipu': 0, 'deepseek': 1, 'model_scope': 2}
        idx = provider_map.get(provider, 0)
        self.provider_combo.setCurrentIndex(idx)
        self.api_stack.setCurrentIndex(idx)
        
        api_settings = self.config.get('api_settings', {})
        for key in ['zhipu', 'deepseek', 'model_scope']:
            s = api_settings.get(key, {})
            getattr(self, f"{key}_api_key").setText(s.get('api_key', ''))
            getattr(self, f"{key}_base_url").setText(s.get('base_url', ''))
            getattr(self, f"{key}_model_name").setText(s.get('model_name', ''))
            
        self.speed_slider.setValue(self.config.get('animation_interval', 150))
        self.scale_slider.setValue(int(self.config.get('pet_scale', 0.5) * 100))
        self.prompt_input.setText(self.config.get('system_prompt', ''))

    def save_settings(self):
        """保存 UI 数据到配置文件"""
        provider_map = {0: 'zhipu', 1: 'deepseek', 2: 'model_scope'}
        self.config['api_provider'] = provider_map[self.provider_combo.currentIndex()]
        
        if 'api_settings' not in self.config:
            self.config['api_settings'] = {}
            
        for key in ['zhipu', 'deepseek', 'model_scope']:
            self.config['api_settings'][key] = {
                'api_key': getattr(self, f"{key}_api_key").text().strip(),
                'base_url': getattr(self, f"{key}_base_url").text().strip(),
                'model_name': getattr(self, f"{key}_model_name").text().strip()
            }
            
        self.config['animation_interval'] = self.speed_slider.value()
        self.config['pet_scale'] = self.scale_slider.value() / 100.0
        self.config['system_prompt'] = self.prompt_input.toPlainText().strip()
        
        if not self.config['system_prompt']:
            self.config['system_prompt'] = "你是一个可爱的桌面宠物助手。"

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            self.settings_changed.emit(self.config)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存配置: {str(e)}")

    # 拖动窗口实现
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
