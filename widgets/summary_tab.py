# -*- coding: utf-8 -*-
"""
周总结模块
"""

import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QMessageBox, QFileDialog, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from utils.icons import svg_pixmap, ICON_REFRESH, ICON_EXPORT


class SummaryTab(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.current_text = ""
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        self.btn_generate = QPushButton("重新生成")
        self.btn_generate.setProperty("class", "primary")
        self.btn_generate.setIcon(QIcon(svg_pixmap(ICON_REFRESH, 14, "#ffffff")))
        self.btn_generate.clicked.connect(self.refresh)
        self.btn_export = QPushButton("导出 TXT")
        self.btn_export.setProperty("class", "btn-sm")
        self.btn_export.setIcon(QIcon(svg_pixmap(ICON_EXPORT, 14, "#475569")))
        self.btn_export.clicked.connect(self.export_txt)
        toolbar.addWidget(self.btn_generate)
        toolbar.addWidget(self.btn_export)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 统计卡片
        stats_group = QGroupBox("本周概览")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(16, 16, 16, 16)

        self.stat_completed = QLabel("0")
        self.stat_inprogress = QLabel("0")
        self.stat_pending = QLabel("0")
        self.stat_todos = QLabel("0")
        self.stat_labels = [
            (self.stat_completed, "已完成项目", "#16a34a"),
            (self.stat_inprogress, "推进中项目", "#2563eb"),
            (self.stat_pending, "待协调事项", "#dc2626"),
            (self.stat_todos, "本周待办", "#f59e0b"),
        ]
        for label, title, color in self.stat_labels:
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"font-size: 34px; font-weight: 700; color: {color};")

        stats_layout.addWidget(QLabel("已完成项目"), 0, 0, Qt.AlignCenter)
        stats_layout.addWidget(self.stat_completed, 1, 0, Qt.AlignCenter)
        stats_layout.addWidget(QLabel("推进中项目"), 0, 1, Qt.AlignCenter)
        stats_layout.addWidget(self.stat_inprogress, 1, 1, Qt.AlignCenter)
        stats_layout.addWidget(QLabel("待协调事项"), 0, 2, Qt.AlignCenter)
        stats_layout.addWidget(self.stat_pending, 1, 2, Qt.AlignCenter)
        stats_layout.addWidget(QLabel("本周待办"), 0, 3, Qt.AlignCenter)
        stats_layout.addWidget(self.stat_todos, 1, 3, Qt.AlignCenter)

        layout.addWidget(stats_group)

        # 总结内容
        content_group = QGroupBox("总结详情")
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(16, 16, 16, 16)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        content_layout.addWidget(self.text_edit)
        layout.addWidget(content_group, stretch=1)

    def refresh(self):
        summary = self.data.weekly_summary()

        self.stat_completed.setText(str(len(summary["completed"])))
        self.stat_inprogress.setText(str(len(summary["in_progress"])))
        self.stat_pending.setText(str(len(summary["pending"])))
        self.stat_todos.setText(str(len(summary["week_todos"])))

        lines = []
        lines.append(f"个人安全工作台 - 周总结")
        lines.append(f"统计周期：{summary['week_start']} 至 {summary['week_end']}")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        lines.append("一、本周已完成项目")
        if not summary["completed"]:
            lines.append("  无")
        for p in summary["completed"]:
            lines.append(f"  ✓ {p.get('name', '')}（负责人：{p.get('owner') or '未分配'}）")
        lines.append("")

        lines.append("二、正在推进的项目")
        if not summary["in_progress"]:
            lines.append("  无")
        for p in summary["in_progress"]:
            deadline_info = f"，截止 {p.get('deadline')}" if p.get('deadline') else ""
            lines.append(f"  → {p.get('name', '')}（负责人：{p.get('owner') or '未分配'}{deadline_info}）")
        lines.append("")

        lines.append("三、待协调事项")
        if not summary["pending"]:
            lines.append("  无")
        for p in summary["pending"]:
            lines.append(f"  ! {p.get('name', '')}")
            if p.get("pending"):
                lines.append(f"    待协调：{p.get('pending')}")
            lines.append(f"    负责人：{p.get('owner') or '未分配'}")
        lines.append("")

        lines.append("四、本周待办统计")
        lines.append(f"  本周待办总数：{len(summary['week_todos'])}")
        lines.append(f"  已完成：{len(summary['done_todos'])}")
        lines.append(f"  未完成：{len(summary['undone_todos'])}")
        if summary["done_todos"]:
            lines.append("  已完成的待办：")
            for t in summary["done_todos"]:
                lines.append(f"    ✓ {t.get('content', '')}")
        if summary["undone_todos"]:
            lines.append("  未完成的待办：")
            for t in summary["undone_todos"]:
                deadline_info = f"（截止 {t.get('deadline')}）" if t.get('deadline') else ""
                lines.append(f"    □ {t.get('content', '')}{deadline_info}")

        self.current_text = "\n".join(lines)
        self.text_edit.setPlainText(self.current_text)

    def export_txt(self):
        if not self.current_text:
            QMessageBox.information(self, "导出", "请先生成周总结")
            return

        default_name = f"周总结_{datetime.now().strftime('%Y-%m-%d')}.txt"
        path, _ = QFileDialog.getSaveFileName(
            self, "导出周总结", default_name, "文本文件 (*.txt)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.current_text)
            QMessageBox.information(self, "导出成功", f"已成功导出到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出失败:\n{str(e)}")
