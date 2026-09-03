# -*- coding: utf-8 -*-
"""
应用设置模块：界面字体大小等偏好，持久化到 Documents/PersonalWorkbench/settings.json
"""

import json
import os

from config import DEFAULT_DATA_DIR

SETTINGS_FILE = os.path.join(DEFAULT_DATA_DIR, "settings.json")

# 字体大小档位
FONT_SCALES = [
    ("小", 0.85),
    ("标准", 1.0),
    ("大", 1.15),
    ("特大", 1.3),
]

DEFAULT_FONT_SCALE = 1.0


class AppSettings:
    """应用设置管理器"""

    def __init__(self, settings_file=None):
        self.settings_file = settings_file or SETTINGS_FILE
        self.font_scale = DEFAULT_FONT_SCALE
        self.load()

    def load(self):
        try:
            if not os.path.exists(self.settings_file):
                return
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            scale = float(data.get("font_scale", DEFAULT_FONT_SCALE))
            if any(abs(scale - s) < 1e-6 for _, s in FONT_SCALES):
                self.font_scale = scale
        except Exception:
            self.font_scale = DEFAULT_FONT_SCALE

    def save(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump({"font_scale": self.font_scale}, f, ensure_ascii=False, indent=2)

    def set_font_scale(self, scale):
        self.font_scale = scale
        self.save()
