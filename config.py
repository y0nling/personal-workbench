# -*- coding: utf-8 -*-
"""
配置模块：定义常量与默认数据
"""

import os

# 应用名称
APP_NAME = "个人工作台"

# 数据版本号
DATA_VERSION = "1.0"

# 数据文件默认路径：放在用户文档目录下，避免 exe 所在目录权限问题
DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "PersonalWorkbench")
DEFAULT_DATA_FILE = os.path.join(DEFAULT_DATA_DIR, "workbench_data.json")

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
