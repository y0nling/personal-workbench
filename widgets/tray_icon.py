# -*- coding: utf-8 -*-
"""
系统托盘图标与菜单
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class TrayIcon(QSystemTrayIcon):
    show_main = pyqtSignal()
    exit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolTip("个人工作台")
        # 由于没有真实图标，使用内嵌风格图标
        self.setIcon(QIcon())

        self.menu = QMenu(parent)

        action_show = QAction("打开主窗口", self)
        action_show.triggered.connect(self.show_main.emit)

        action_exit = QAction("退出", self)
        action_exit.triggered.connect(self.exit_app.emit)

        self.menu.addAction(action_show)
        self.menu.addSeparator()
        self.menu.addAction(action_exit)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main.emit()
