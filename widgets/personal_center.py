# -*- coding: utf-8 -*-
"""
个人中心模块：修改密码、恢复默认密码、界面字体大小设置
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt

from utils.settings import FONT_SCALES


class PersonalCenterTab(QWidget):
    """个人中心标签页"""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.auth = None  # 登录成功后由主窗口注入
        self.settings = settings
        self._build_ui()

    def set_auth(self, auth):
        """注入认证管理器（登录成功后由主窗口调用）"""
        self.auth = auth

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ===== 修改密码 =====
        group_pwd = QGroupBox("修改密码")
        pwd_layout = QVBoxLayout(group_pwd)
        pwd_layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("原密码："))
        self.input_old = QLineEdit()
        self.input_old.setEchoMode(QLineEdit.Password)
        row1.addWidget(self.input_old)
        pwd_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("新密码："))
        self.input_new = QLineEdit()
        self.input_new.setEchoMode(QLineEdit.Password)
        row2.addWidget(self.input_new)
        pwd_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("确认密码："))
        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.Password)
        row3.addWidget(self.input_confirm)
        pwd_layout.addLayout(row3)

        btn_change = QPushButton("修改密码")
        btn_change.setProperty("class", "primary")
        btn_change.clicked.connect(self.change_password)
        pwd_layout.addWidget(btn_change, alignment=Qt.AlignLeft)

        layout.addWidget(group_pwd)

        # ===== 恢复默认密码 =====
        group_reset = QGroupBox("恢复默认密码")
        reset_layout = QVBoxLayout(group_reset)
        btn_reset = QPushButton("恢复为默认密码（123456）")
        btn_reset.clicked.connect(self.reset_password)
        reset_layout.addWidget(btn_reset, alignment=Qt.AlignLeft)
        layout.addWidget(group_reset)

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

    def change_password(self):
        old = self.input_old.text()
        new = self.input_new.text()
        confirm = self.input_confirm.text()
        if not new:
            QMessageBox.warning(self, "提示", "新密码不能为空")
            return
        if new != confirm:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            return
        ok, msg = self.auth.change_password(old, new)
        if ok:
            QMessageBox.information(self, "成功", msg)
            self.input_old.clear()
            self.input_new.clear()
            self.input_confirm.clear()
        else:
            QMessageBox.warning(self, "失败", msg)

    def reset_password(self):
        reply = QMessageBox.question(
            self, "确认", "确定将密码恢复为默认密码 123456 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.auth.reset_password()
            QMessageBox.information(self, "成功", "已恢复默认密码：123456")

    def on_font_changed(self, index):
        scale = self.combo_font.itemData(index)
        self.settings.set_font_scale(scale)
        QMessageBox.information(
            self, "提示",
            "字体大小已调整，重启应用后生效。"
        )
