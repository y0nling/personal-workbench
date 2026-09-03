# -*- coding: utf-8 -*-
"""
桌面右侧贴边小面板：显示 TOP 待办、推进中项目、待协调事项
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from utils.icons import svg_pixmap, ICON_PIN, ICON_PIN_SLASH, ICON_MAXIMIZE


class SidePanel(QWidget):
    """右侧贴边小面板"""
    clicked = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setFixedWidth(260)
        self.setMinimumHeight(220)
        self.is_pinned = True
        self.setup_ui()
        self.position_to_right()

        # 自动刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)  # 每分钟刷新

        self.refresh()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
                border-radius: 8px;
                color: #f8fafc;
            }
            QLabel {
                color: #f8fafc;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # 标题栏
        header = QHBoxLayout()
        self.title = QLabel("安全工作台")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(13)
        self.title.setFont(title_font)
        header.addWidget(self.title)

        self.btn_pin = QPushButton()
        self.btn_pin.setFixedSize(28, 28)
        self.btn_pin.setToolTip("已固定")
        self.btn_pin.setStyleSheet("QPushButton { background-color: #334155; border-radius: 4px; padding: 0; }")
        self.btn_pin.setIcon(QIcon(svg_pixmap(ICON_PIN, 14, "#f8fafc")))
        self.btn_pin.clicked.connect(self.toggle_pin)
        header.addWidget(self.btn_pin)
        layout.addLayout(header)

        # 统计行
        self.stats_label = QLabel("待办 0 | 推进 0 | 协调 0")
        self.stats_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self.stats_label)

        # TOP 待办
        todo_title = QLabel("TOP 待办")
        todo_title.setStyleSheet("font-weight: bold; color: #60a5fa; margin-top: 6px;")
        layout.addWidget(todo_title)
        self.todo_list = QVBoxLayout()
        self.todo_list.setSpacing(6)
        layout.addLayout(self.todo_list)

        # 推进中项目
        project_title = QLabel("推进中项目")
        project_title.setStyleSheet("font-weight: bold; color: #4ade80; margin-top: 6px;")
        layout.addWidget(project_title)
        self.project_list = QVBoxLayout()
        self.project_list.setSpacing(6)
        layout.addLayout(self.project_list)

        # 待协调事项
        pending_title = QLabel("待协调事项")
        pending_title.setStyleSheet("font-weight: bold; color: #f87171; margin-top: 6px;")
        layout.addWidget(pending_title)
        self.pending_list = QVBoxLayout()
        self.pending_list.setSpacing(6)
        layout.addLayout(self.pending_list)

        layout.addStretch()

        # 展开主窗口按钮
        self.btn_open = QPushButton("打开主窗口")
        self.btn_open.setIcon(QIcon(svg_pixmap(ICON_MAXIMIZE, 14, "#f8fafc")))
        self.btn_open.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn_open)

    def position_to_right(self):
        """定位到屏幕右侧"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 8, screen.top() + 120)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.btn_pin.setIcon(QIcon(svg_pixmap(ICON_PIN, 14, "#f8fafc")))
            self.btn_pin.setToolTip("已固定")
        else:
            self.btn_pin.setIcon(QIcon(svg_pixmap(ICON_PIN_SLASH, 14, "#f8fafc")))
            self.btn_pin.setToolTip("未固定")

    def refresh(self):
        """刷新面板数据"""
        todos = [t for t in self.data.sorted_todos() if t.get("status") == "未完成"][:3]
        in_progress = [p for p in self.data.projects if p.get("status") == "进行中"][:3]
        pending = [p for p in self.data.projects if p.get("status") == "待协调" or (p.get("pending") and p.get("pending").strip())][:3]

        self.stats_label.setText(
            f"待办 {len([t for t in self.data.todos if t.get('status') == '未完成'])} | "
            f"推进 {len([p for p in self.data.projects if p.get('status') == '进行中'])} | "
            f"协调 {len(pending)}"
        )

        self._fill_list(self.todo_list, todos, "content", "□")
        self._fill_list(self.project_list, in_progress, "name", "→")
        self._fill_list(self.pending_list, pending, "name", "!", extra_key="pending")

    def _fill_list(self, layout, items, key, prefix, extra_key=None):
        """清空并填充列表"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not items:
            label = QLabel("暂无")
            label.setStyleSheet("color: #64748b; font-size: 12px;")
            layout.addWidget(label)
            return

        for item in items:
            text = item.get(key, "") or "-"
            if extra_key and item.get(extra_key):
                text += f" | {item.get(extra_key)}"
            label = QLabel(f"{prefix} {text}")
            label.setStyleSheet("color: #e2e8f0; font-size: 12px; padding-left: 4px;")
            label.setWordWrap(True)
            label.setToolTip(text)
            layout.addWidget(label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
