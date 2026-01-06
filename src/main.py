#!/usr/bin/env python3
"""
桌面宠物应用主程序
使用 PyQt6 实现的可爱桌面宠物

特性：
- 半透明暖色调主题
- 图片轮播动画
- AI 文本聊天（智谱 AI）
- 可拖拽、可交互
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from src.pet_widget import PetWidget
from src.logger import setup_logging


def get_config_path() -> str:
    """获取配置文件路径"""
    return os.path.join(PROJECT_ROOT, "config.json")


def load_config() -> dict:
    """加载配置"""
    config_path = get_config_path()
    default_config = {
        "api_key": "YOUR_API_KEY_HERE",
        "model": "glm-4.6",
        "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "system_prompt": "你是一个可爱的桌面宠物助手，性格温柔、活泼、乐于助人。请用简短、可爱的语气回复用户，回复控制在50字以内。",
        "animation_interval": 150,
        "pet_scale": 0.5
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置（补充缺失的键）
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    # 创建默认配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"创建配置文件失败: {e}")
    
    return default_config


def get_assets_path() -> str:
    """获取资源目录路径"""
    return os.path.join(PROJECT_ROOT, "assets")


def setup_tray_icon(app: QApplication, pet_widget: PetWidget) -> QSystemTrayIcon:
    """设置系统托盘图标"""
    tray = QSystemTrayIcon()
    
    # 尝试加载图标
    icon_path = os.path.join(get_assets_path(), "expressions", "icon")
    icon_file = None
    
    if os.path.exists(icon_path):
        for f in os.listdir(icon_path):
            if f.endswith(('.png', '.ico', '.jpg')):
                icon_file = os.path.join(icon_path, f)
                break
    
    if icon_file and os.path.exists(icon_file):
        tray.setIcon(QIcon(icon_file))
    else:
        # 使用默认图标（从第一帧动画获取）
        if pet_widget.animation_frames:
            first_action = list(pet_widget.animation_frames.keys())[0]
            if pet_widget.animation_frames[first_action]:
                first_frame = pet_widget.animation_frames[first_action][0]
                tray.setIcon(QIcon(first_frame))
    
    tray.setToolTip("桌面宠物 🐾")
    
    # 创建托盘菜单
    tray_menu = QMenu()
    
    show_action = QAction("显示宠物", tray_menu)
    show_action.triggered.connect(pet_widget.show)
    tray_menu.addAction(show_action)
    
    hide_action = QAction("隐藏宠物", tray_menu)
    hide_action.triggered.connect(pet_widget.hide)
    tray_menu.addAction(hide_action)
    
    tray_menu.addSeparator()
    
    think_action = QAction("强制思考 💭", tray_menu)
    think_action.triggered.connect(pet_widget.send_brain_message)
    tray_menu.addAction(think_action)
    
    settings_action = QAction("设置", tray_menu)
    settings_action.triggered.connect(pet_widget.show_settings)
    tray_menu.addAction(settings_action)
    
    tray_menu.addSeparator()
    
    quit_action = QAction("退出", tray_menu)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    
    tray.setContextMenu(tray_menu)
    tray.activated.connect(lambda reason: pet_widget.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    
    return tray


def main():
    """主函数"""
    # 启用高 DPI 缩放
    # PyQt6 默认启用高 DPI 支持
    
    # 初始化日志系统
    setup_logging("pet.log")
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("桌面宠物")
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出应用
    
    # 加载配置
    config = load_config()
    config_path = get_config_path()
    assets_path = get_assets_path()
    
    # 检查资源目录
    if not os.path.exists(assets_path):
        print(f"错误: 资源目录不存在: {assets_path}")
        print("请确保 assets/actions 目录包含宠物动画帧图片")
        sys.exit(1)
    
    # 创建宠物窗口
    pet = PetWidget(assets_path, config, config_path)
    pet.show()
    
    # 设置系统托盘
    tray = setup_tray_icon(app, pet)
    tray.show()
    
    # 显示欢迎消息
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(500, lambda: pet._show_bubble("你好呀！我是你的桌面宠物~ 以后我会自己说话啦，你可以右键点击我来互动哦！", duration=5000))
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
