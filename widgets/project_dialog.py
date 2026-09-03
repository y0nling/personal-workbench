# -*- coding: utf-8 -*-
"""
项目编辑对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTextEdit, QPushButton, QFormLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate

from config import PROJECT_STATUSES


class ProjectDialog(QDialog):
    def __init__(self, data, project=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.project = project
        self.setWindowTitle("编辑项目" if project else "新增项目")
        self.setMinimumWidth(600)
        self.setup_ui()
        if project:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入项目名称")
        form.addRow("项目名称 *", self.name_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(PROJECT_STATUSES)
        form.addRow("项目状态", self.status_combo)

        self.owner_combo = QComboBox()
        self.owner_combo.addItem("请选择", "")
        for person in self.data.people:
            self.owner_combo.addItem(person, person)
        form.addRow("负责人", self.owner_combo)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setSpecialValueText("未设置")
        form.addRow("开始时间", self.start_date_edit)

        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_edit.setDate(QDate.currentDate())
        self.deadline_edit.setSpecialValueText("未设置")
        form.addRow("截止日期", self.deadline_edit)

        self.pending_input = QTextEdit()
        self.pending_input.setPlaceholderText("如有需要协调的事项，请在此填写")
        self.pending_input.setMaximumHeight(80)
        form.addRow("待协调事项", self.pending_input)

        self.remark_input = QTextEdit()
        self.remark_input.setPlaceholderText("其他补充说明")
        self.remark_input.setMaximumHeight(80)
        form.addRow("备注", self.remark_input)

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
        p = self.project
        self.name_input.setText(p.get("name", ""))
        self.status_combo.setCurrentText(p.get("status", "未开始"))
        owner = p.get("owner", "")
        index = self.owner_combo.findData(owner)
        self.owner_combo.setCurrentIndex(index if index >= 0 else 0)
        start_date = p.get("startDate", "")
        if start_date:
            try:
                self.start_date_edit.setDate(QDate.fromString(start_date, "yyyy-MM-dd"))
            except Exception:
                pass
        else:
            self.start_date_edit.setDate(QDate())
            self.start_date_edit.clear()
        deadline = p.get("deadline", "")
        if deadline:
            try:
                self.deadline_edit.setDate(QDate.fromString(deadline, "yyyy-MM-dd"))
            except Exception:
                pass
        else:
            self.deadline_edit.setDate(QDate())
            self.deadline_edit.clear()
        self.pending_input.setPlainText(p.get("pending", ""))
        self.remark_input.setPlainText(p.get("remark", ""))

    def get_data(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd") if self.start_date_edit.date().isValid() and not self.start_date_edit.date().isNull() else ""
        deadline = self.deadline_edit.date().toString("yyyy-MM-dd") if self.deadline_edit.date().isValid() and not self.deadline_edit.date().isNull() else ""
        return {
            "name": self.name_input.text().strip(),
            "status": self.status_combo.currentText(),
            "owner": self.owner_combo.currentData() or "",
            "startDate": start_date,
            "deadline": deadline,
            "pending": self.pending_input.toPlainText().strip(),
            "remark": self.remark_input.toPlainText().strip(),
        }

    def accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "输入错误", "请输入项目名称")
            return
        super().accept()
