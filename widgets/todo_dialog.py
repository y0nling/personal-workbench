# -*- coding: utf-8 -*-
"""
待办编辑对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QFormLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate

from config import TODO_STATUSES


class TodoDialog(QDialog):
    def __init__(self, data, todo=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.todo = todo
        self.setWindowTitle("编辑待办" if todo else "新增待办")
        self.setMinimumWidth(500)
        self.setup_ui()
        if todo:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.content_input = QLineEdit()
        self.content_input.setPlaceholderText("请输入待办内容")
        form.addRow("待办内容 *", self.content_input)

        self.owner_combo = QComboBox()
        self.owner_combo.addItem("请选择", "")
        for person in self.data.people:
            self.owner_combo.addItem(person, person)
        form.addRow("负责人", self.owner_combo)

        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_edit.setDate(QDate.currentDate())
        self.deadline_edit.setSpecialValueText("未设置")
        form.addRow("截止时间", self.deadline_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(TODO_STATUSES)
        form.addRow("状态", self.status_combo)

        self.project_combo = QComboBox()
        self.project_combo.addItem("无", "")
        for p in self.data.projects:
            self.project_combo.addItem(p.get("name", ""), p.get("id", ""))
        form.addRow("关联项目", self.project_combo)

        layout.addLayout(form)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton("保存")
        self.btn_save.setProperty("class", "primary")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def load_data(self):
        t = self.todo
        self.content_input.setText(t.get("content", ""))
        owner = t.get("owner", "")
        index = self.owner_combo.findData(owner)
        self.owner_combo.setCurrentIndex(index if index >= 0 else 0)
        deadline = t.get("deadline", "")
        if deadline:
            try:
                self.deadline_edit.setDate(QDate.fromString(deadline, "yyyy-MM-dd"))
            except Exception:
                pass
        else:
            self.deadline_edit.setDate(QDate())
            self.deadline_edit.clear()
        self.status_combo.setCurrentText(t.get("status", "未完成"))
        project_id = t.get("projectId", "")
        index = self.project_combo.findData(project_id)
        self.project_combo.setCurrentIndex(index if index >= 0 else 0)

    def get_data(self):
        deadline = self.deadline_edit.date().toString("yyyy-MM-dd") if self.deadline_edit.date().isValid() and not self.deadline_edit.date().isNull() else ""
        return {
            "content": self.content_input.text().strip(),
            "owner": self.owner_combo.currentData() or "",
            "deadline": deadline,
            "status": self.status_combo.currentText(),
            "projectId": self.project_combo.currentData() or "",
        }

    def accept(self):
        if not self.content_input.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入待办内容")
            return
        super().accept()
