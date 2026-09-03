# -*- coding: utf-8 -*-
"""
项目看板模块
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QSize
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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "序号", "项目名称", "状态", "负责人", "项目成员", "开始时间", "截止日期",
            "待协调事项", "备注", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in [0, 2, 3, 4, 5, 6]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        # 操作列固定宽度，避免按钮被挤压
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 100)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        # 行高必须大于按钮尺寸 + QSS padding 引起的 sizeHint 高度，避免按钮被垂直压缩
        self.table.verticalHeader().setDefaultSectionSize(56)
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

            self.table.setItem(i, 3, QTableWidgetItem("、".join(p.get("owner") or []) or "-"))
            self.table.setItem(i, 4, QTableWidgetItem("、".join(p.get("members") or []) or "-"))
            self.table.setItem(i, 5, QTableWidgetItem(p.get("startDate", "") or "-"))
            self.table.setItem(i, 6, QTableWidgetItem(p.get("deadline", "") or "-"))
            self.table.setItem(i, 7, QTableWidgetItem(p.get("pending", "") or "-"))
            self.table.setItem(i, 8, QTableWidgetItem(p.get("remark", "") or "-"))

            # 操作按钮：用 上下stretch 让按钮按固定尺寸自然垂直居中，
            # 避免 QHBoxLayout+addStretch 依赖按钮 sizeHint 导致高度被压缩。
            btn_edit = QPushButton()
            btn_edit.setFixedSize(34, 34)
            btn_edit.setIcon(QIcon(svg_pixmap(ICON_EDIT, 18, "#2563eb")))
            btn_edit.setIconSize(QSize(18, 18))
            btn_edit.setFlat(True)
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setToolTip("编辑项目")
            # 显式覆盖全局 QSS 的 min-height 和 padding，防止按钮被撑到 44px 高
            btn_edit.setStyleSheet(
                "QPushButton { border: none; background: transparent; border-radius: 9px;"
                " min-height: 0px; min-width: 0px; padding: 0px; }"
                "QPushButton:hover { background-color: #eff6ff; }"
            )
            btn_edit.clicked.connect(lambda _, pid=p["id"]: self.edit_project(pid))

            btn_delete = QPushButton()
            btn_delete.setFixedSize(34, 34)
            btn_delete.setIcon(QIcon(svg_pixmap(ICON_DELETE, 18, "#dc2626")))
            btn_delete.setIconSize(QSize(18, 18))
            btn_delete.setFlat(True)
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.setToolTip("删除项目")
            btn_delete.setStyleSheet(
                "QPushButton { border: none; background: transparent; border-radius: 9px;"
                " min-height: 0px; min-width: 0px; padding: 0px; }"
                "QPushButton:hover { background-color: #fef2f2; }"
            )
            btn_delete.clicked.connect(lambda _, pid=p["id"]: self.delete_project(pid))

            # 水平子布局放两个按钮，外层垂直布局加 stretch 保证垂直居中
            btn_row = QWidget()
            btn_row_layout = QHBoxLayout(btn_row)
            btn_row_layout.setContentsMargins(0, 0, 0, 0)
            btn_row_layout.setSpacing(8)
            btn_row_layout.addStretch()
            btn_row_layout.addWidget(btn_edit)
            btn_row_layout.addWidget(btn_delete)
            btn_row_layout.addStretch()

            op_widget = QWidget()
            op_layout = QVBoxLayout(op_widget)
            op_layout.setContentsMargins(4, 0, 4, 0)
            op_layout.setSpacing(0)
            op_layout.addStretch()
            op_layout.addWidget(btn_row)
            op_layout.addStretch()
            self.table.setCellWidget(i, 9, op_widget)

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
