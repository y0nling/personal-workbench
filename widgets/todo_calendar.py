# -*- coding: utf-8 -*-
"""
待办月历视图：自绘当月日期网格，标注每天待办及其完成/逾期状态
"""

from datetime import datetime, date, timedelta

from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

from utils.icons import svg_pixmap, ICON_CHEVRON_LEFT, ICON_CHEVRON_RIGHT

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]


class DayCell(QFrame):
    """单个日期格：日期数字 + 当天待办事项条目"""

    clicked = pyqtSignal(str)  # 传出 yyyy-MM-dd

    def __init__(self, day_date, todos, is_today, parent=None):
        super().__init__(parent)
        self.day_str = day_date.strftime("%Y-%m-%d")
        self.setObjectName("dayCell")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(74)
        self.setCursor(Qt.PointingHandCursor)

        in_month = day_date.month == self._anchor_month()
        today = is_today

        # 底色：今天高亮，非本月置灰
        if today:
            bg = "#dbeafe"
            border = "#2563eb"
        elif not in_month:
            bg = "#f8fafc"
            border = "#e2e8f0"
        else:
            bg = "#ffffff"
            border = "#e2e8f0"

        self.setStyleSheet(
            f"QFrame#dayCell {{ background-color: {bg};"
            f" border: 1px solid {border}; border-radius: 8px; }}"
            f"QFrame#dayCell:hover {{ border: 1px solid #2563eb; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 5, 6, 5)
        lay.setSpacing(2)

        # 日期数字
        num_color = "#2563eb" if today else ("#94a3b8" if not in_month else "#1e293b")
        lbl_num = QLabel(str(day_date.day))
        lbl_num.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {num_color}; background: transparent; border: none;")
        lay.addWidget(lbl_num)

        # 当天待办条目（最多显示 3 条，超出显示 +N）
        shown = todos[:3]
        for t in shown:
            done = t.get("status") == "已完成"
            overdue = False
            if not done and t.get("deadline"):
                try:
                    overdue = datetime.now() > datetime.fromisoformat(t["deadline"])
                except Exception:
                    pass
            if done:
                fg, deco = "#16a34a", "line-through"
            elif overdue:
                fg, deco = "#dc2626", "none"
            else:
                fg, deco = "#334155", "none"
            text = t.get("content", "")
            if len(text) > 6:
                text = text[:6] + "…"
            lbl = QLabel("• " + text)
            lbl.setStyleSheet(
                f"font-size: 11px; color: {fg}; background: transparent; border: none;"
                f" text-decoration: {deco};"
            )
            lay.addWidget(lbl)

        if len(todos) > 3:
            more = QLabel(f"+{len(todos) - 3}")
            more.setStyleSheet("font-size: 11px; color: #2563eb; background: transparent; border: none; font-weight: 600;")
            lay.addWidget(more)

        lay.addStretch()

    def _anchor_month(self):
        # 由父组件注入当前展示月；这里通过属性读取
        return self.property("anchorMonth")

    def mousePressEvent(self, event):
        self.clicked.emit(self.day_str)
        super().mousePressEvent(event)


class TodoCalendar(QWidget):
    """月历视图：标题栏（月份 + 左右切换）+ 星期头 + 日期网格"""

    day_clicked = pyqtSignal(str)  # yyyy-MM-dd

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        today = date.today()
        self.display_year = today.year
        self.display_month = today.month
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # 标题栏：‹ 2026年9月 ›
        header = QHBoxLayout()
        header.setSpacing(8)
        self.btn_prev = QPushButton()
        self.btn_prev.setFixedSize(30, 30)
        self.btn_prev.setIcon(QIcon(svg_pixmap(ICON_CHEVRON_LEFT, 14, "#475569")))
        self.btn_prev.setIconSize(QSize(14, 14))
        self.btn_prev.setFlat(True)
        self.btn_prev.setToolTip("上一月")
        self.btn_prev.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 6px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        self.btn_prev.clicked.connect(self.prev_month)

        self.lbl_month = QLabel("")
        self.lbl_month.setStyleSheet("font-size: 16px; font-weight: 600; color: #1e293b;")
        header.addWidget(self.btn_prev)
        header.addWidget(self.lbl_month)
        header.addStretch()

        self.btn_today = QPushButton("今天")
        self.btn_today.setProperty("class", "btn-sm")
        self.btn_today.clicked.connect(self.go_today)
        header.addWidget(self.btn_today)

        self.btn_next = QPushButton()
        self.btn_next.setFixedSize(30, 30)
        self.btn_next.setIcon(QIcon(svg_pixmap(ICON_CHEVRON_RIGHT, 14, "#475569")))
        self.btn_next.setIconSize(QSize(14, 14))
        self.btn_next.setFlat(True)
        self.btn_next.setToolTip("下一月")
        self.btn_next.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 6px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        self.btn_next.clicked.connect(self.next_month)
        header.addWidget(self.btn_next)

        root.addLayout(header)

        # 星期头
        weekday_row = QGridLayout()
        weekday_row.setSpacing(6)
        for i, wd in enumerate(WEEKDAYS):
            lbl = QLabel(wd)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 13px; color: #64748b; font-weight: 600; padding: 2px 0;")
            weekday_row.addWidget(lbl, 0, i)
        root.addLayout(weekday_row)

        # 日期网格
        self.grid = QGridLayout()
        self.grid.setSpacing(6)
        root.addLayout(self.grid, 1)

    def go_today(self):
        today = date.today()
        self.display_year = today.year
        self.display_month = today.month
        self.refresh()

    def prev_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1
        self.refresh()

    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1
        self.refresh()

    def refresh(self):
        # 清空旧格子
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.lbl_month.setText(f"{self.display_year} 年 {self.display_month} 月")

        # 当月 1 号
        first = date(self.display_year, self.display_month, 1)
        # 周一为起点：weekday() 周一=0
        start = first - timedelta(days=first.weekday())

        today_str = date.today().strftime("%Y-%m-%d")

        # 待办按截止日期分组
        todos_by_day = {}
        for t in self.data.todos:
            dl = t.get("deadline")
            if not dl:
                continue
            try:
                d = datetime.fromisoformat(dl).strftime("%Y-%m-%d")
            except Exception:
                continue
            todos_by_day.setdefault(d, []).append(t)

        # 6 行 × 7 列
        for row in range(6):
            for col in range(7):
                day = start + timedelta(days=row * 7 + col)
                day_str = day.strftime("%Y-%m-%d")
                todos = todos_by_day.get(day_str, [])
                cell = DayCell(day, todos, day_str == today_str)
                cell.setProperty("anchorMonth", self.display_month)
                cell.clicked.connect(self.day_clicked.emit)
                self.grid.addWidget(cell, row, col)
