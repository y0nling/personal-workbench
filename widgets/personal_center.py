# -*- coding: utf-8 -*-
"""
设置模块：界面字体大小设置
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt

from utils.settings import FONT_SCALES


class PersonalCenterTab(QWidget):
    """设置标签页（保留原类名，仅保留界面设置功能）"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ===== 界面设置 =====
        group_ui = QGroupBox("界面设置")
        ui_layout = QHBoxLayout(group_ui)
        ui_layout.addWidget(QLabel("字体大小："))
        self.combo_font = QComboBox()
        for label, scale in FONT_SCALES:
            self.combo_font.addItem(label, scale)
        # 选中当前档位
        for i, (_, scale) in enumerate(FONT_SCALES):
            if abs(scale - self.settings.font_scale) < 1e-6:
                self.combo_font.setCurrentIndex(i)
                break
        self.combo_font.currentIndexChanged.connect(self.on_font_changed)
        ui_layout.addWidget(self.combo_font)
        ui_layout.addStretch()
        layout.addWidget(group_ui)

        layout.addStretch()

    def on_font_changed(self, index):
        scale = self.combo_font.itemData(index)
        self.settings.set_font_scale(scale)
        # 弹窗确认：暂不重启 / 马上重启
        msg = QMessageBox(self)
        msg.setWindowTitle("字体大小已调整")
        msg.setText("字体大小已修改，需要重启应用后生效。")
        btn_restart = msg.addButton("马上重启", QMessageBox.AcceptRole)
        btn_later = msg.addButton("暂不重启", QMessageBox.RejectRole)
        msg.setDefaultButton(btn_later)
        msg.exec_()
        if msg.clickedButton() == btn_restart:
            self._restart_app()

    def _restart_app(self):
        """重启应用：启动新进程后退出当前进程"""
        import sys
        import os
        import subprocess
        exe = sys.executable
        # PyInstaller 打包后为 exe，开发时为 python main.py
        if getattr(sys, "frozen", False):
            cmd = [exe]
        else:
            cmd = [exe, "main.py"]
        # 分离启动新进程
        if sys.platform == "win32":
            subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS, close_fds=True)
        else:
            subprocess.Popen(cmd, start_new_session=True)
        # 退出当前应用
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()
