# -*- coding: utf-8 -*-
"""
人员管理模块
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from utils.icons import svg_pixmap, ICON_USER, ICON_DELETE


class PeopleTab(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        self.btn_add = QPushButton("新增人员")
        self.btn_add.setProperty("class", "primary")
        self.btn_add.setIcon(QIcon(svg_pixmap(ICON_USER, 14, "#ffffff")))
        self.btn_add.clicked.connect(self.add_person)
        toolbar.addWidget(self.btn_add)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["序号", "姓名", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # 操作列固定宽度，避免按钮被挤压
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 80)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        layout.addWidget(self.table)

    def refresh(self):
        self.table.setRowCount(len(self.data.people))
        for i, person in enumerate(self.data.people):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(person))

            # 操作按钮：纯图标，居中放置，自动适应当前行高
            op_widget = QWidget()
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(4, 0, 4, 0)
            op_layout.setSpacing(0)

            btn_delete = QPushButton()
            btn_delete.setFixedSize(36, 36)
            btn_delete.setIcon(QIcon(svg_pixmap(ICON_DELETE, 18, "#dc2626")))
            btn_delete.setIconSize(QSize(18, 18))
            btn_delete.setFlat(True)
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.setToolTip(f"删除人员【{person}】")
            btn_delete.setStyleSheet(
                "QPushButton { border: none; background: transparent; border-radius: 10px; }"
                "QPushButton:hover { background-color: #fef2f2; }"
            )
            btn_delete.clicked.connect(lambda _, name=person: self.delete_person(name))

            op_layout.addStretch()
            op_layout.addWidget(btn_delete)
            op_layout.addStretch()
            self.table.setCellWidget(i, 2, op_widget)

    def add_person(self):
        name, ok = QInputDialog.getText(self, "新增人员", "请输入人员姓名：")
        if ok and name.strip():
            try:
                self.data.add_person(name)
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "新增失败", str(e))

    def delete_person(self, name):
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定删除人员【{name}】吗？\n该人员负责的项目和待办将被置为未分配。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.data.delete_person(name)
            self.refresh()
