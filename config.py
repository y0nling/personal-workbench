# -*- coding: utf-8 -*-
"""
配置模块：定义常量与默认数据
"""

import os
import sys

# 应用名称
APP_NAME = "个人工作台"

# 数据版本号
DATA_VERSION = "1.0"

# 数据文件路径：放在 exe 同级目录，整个工具文件夹自包含可便携
def _get_data_dir():
    """获取数据目录：打包后取 exe 所在目录，开发时取项目根目录（config.py 所在目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后：exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境：config.py 所在目录即项目根
        return os.path.dirname(os.path.abspath(__file__))

DEFAULT_DATA_DIR = _get_data_dir()
DEFAULT_DATA_FILE = os.path.join(DEFAULT_DATA_DIR, "workbench_data.json")
SETTINGS_FILE = os.path.join(DEFAULT_DATA_DIR, "settings.json")

# 默认人员
DEFAULT_PEOPLE = [
    "殷雪峰",
    "吕杰",
    "姚泽泽",
]

# 项目状态
PROJECT_STATUSES = ["未开始", "进行中", "待协调", "已完成", "暂停"]

# 待办状态
TODO_STATUSES = ["未完成", "已完成"]
