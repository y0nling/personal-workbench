# -*- coding: utf-8 -*-
"""
项目看板模块
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon

from models import short_datetime
from widgets.project_dialog import ProjectDialog
from widgets.export_xlsx_dialog import export_projects_to_xlsx
from utils.icons import svg_pixmap, ICON_PLUS, ICON_EXPORT, ICON_EDIT, ICON_DELETE


class ProjectTab(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        self.btn_add = QPushButton("新增项目")
        self.btn_add.setProperty("class", "primary")
        self.btn_add.setIcon(QIcon(svg_pixmap(ICON_PLUS, 14, "#ffffff")))
        self.btn_add.clicked.connect(self.add_project)
        toolbar.addWidget(self.btn_add)
        toolbar.addStretch()

        self.btn_export = QPushButton("导出 Excel")
        self.btn_export.setProperty("class", "btn-sm")
        self.btn_export.setIcon(QIcon(svg_pixmap(ICON_EXPORT, 14, "#475569")))
        self.btn_export.clicked.connect(self.export_xlsx)
        toolbar.addWidget(self.btn_export)

        layout.addLayout(toolbar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "序号", "项目名称", "状态", "负责人", "截止日期",
            "待协调事项", "创建时间", "最后更新", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def refresh(self):
        projects = self.data.sorted_projects()
        self.table.setRowCount(len(projects))

        for i, p in enumerate(projects):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(p.get("name", "")))

            status_item = QTableWidgetItem(p.get("status", ""))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.set_status_style(status_item, p.get("status", ""))
            self.table.setItem(i, 2, status_item)

            self.table.setItem(i, 3, QTableWidgetItem(p.get("owner", "") or "-"))
            self.table.setItem(i, 4, QTableWidgetItem(p.get("deadline", "") or "-"))
            self.table.setItem(i, 5, QTableWidgetItem(p.get("pending", "") or "-"))
            self.table.setItem(i, 6, QTableWidgetItem(short_datetime(p.get("createdAt", ""))))
            self.table.setItem(i, 7, QTableWidgetItem(short_datetime(p.get("updatedAt", ""))))

            # 操作按钮
            op_widget = QWidget()
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(4, 2, 4, 2)
            op_layout.setSpacing(6)

            btn_edit = QPushButton("编辑")
            btn_edit.setProperty("class", "btn-sm")
            btn_edit.setIcon(QIcon(svg_pixmap(ICON_EDIT, 14, "#2563eb")))
            btn_edit.clicked.connect(lambda _, pid=p["id"]: self.edit_project(pid))

            btn_delete = QPushButton("删除")
            btn_delete.setProperty("class", "danger btn-sm")
            btn_delete.setIcon(QIcon(svg_pixmap(ICON_DELETE, 14, "#dc2626")))
            btn_delete.clicked.connect(lambda _, pid=p["id"]: self.delete_project(pid))

            op_layout.addWidget(btn_edit)
            op_layout.addWidget(btn_delete)
            self.table.setCellWidget(i, 8, op_widget)

    def set_status_style(self, item, status):
        colors = {
            "未开始": "#64748b",
            "进行中": "#2563eb",
            "待协调": "#dc2626",
            "已完成": "#16a34a",
            "暂停": "#6b7280",
        }
        item.setForeground(__import__("PyQt5.QtGui").QtGui.QColor(colors.get(status, "#1e293b")))
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignCenter)

    def add_project(self):
        dialog = ProjectDialog(self.data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.data.add_project(**dialog.get_data())
            self.refresh()

    def edit_project(self, project_id):
        project = next((p for p in self.data.projects if p["id"] == project_id), None)
        if not project:
            return
        dialog = ProjectDialog(self.data, project=project, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.data.update_project(project_id, **dialog.get_data())
            self.refresh()

    def delete_project(self, project_id):
        reply = QMessageBox.question(
            self, "确认删除", "确定删除此项目吗？相关待办将不再关联该项目。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.data.delete_project(project_id)
            self.refresh()

    def export_xlsx(self):
        export_projects_to_xlsx(self.data, self)
