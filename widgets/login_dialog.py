# -*- coding: utf-8 -*-
"""
登录窗口模块：启动时账号密码登录
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)
from PyQt5.QtCore import Qt

from utils.auth import AuthManager
from utils.icons import app_icon


class LoginDialog(QDialog):
    """登录对话框，登录成功 accept()，退出 reject()"""

    def __init__(self, auth: AuthManager, parent=None):
        super().__init__(parent)
        self.auth = auth
        self.setWindowTitle("登录 - 个人工作台")
        self.setWindowIcon(app_icon())
        self.setFixedSize(360, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)

        title = QLabel("个人工作台")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1e293b;")
        layout.addWidget(title)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("账号")
        layout.addWidget(self.input_user)

        self.input_pwd = QLineEdit()
        self.input_pwd.setPlaceholderText("密码")
        self.input_pwd.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_pwd)

        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color:#dc2626;")
        layout.addWidget(self.label_error)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.btn_login = QPushButton("登 录")
        self.btn_login.setProperty("class", "primary")
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self.try_login)
        self.btn_cancel = QPushButton("退 出")
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_login)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

    def try_login(self):
        username = self.input_user.text().strip()
        password = self.input_pwd.text()
        if not username or not password:
            self.label_error.setText("请输入账号和密码")
            return
        if self.auth.verify(username, password):
            self.accept()
        else:
            self.label_error.setText("账号或密码错误")
            self.input_pwd.clear()
            self.input_pwd.setFocus()
