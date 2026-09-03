# -*- coding: utf-8 -*-
"""
待办月历侧栏：自绘当月日期网格，每天以彩色圆点标注待办状态
窄条紧凑布局，配合右侧待办列表使用
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
    """单个日期格：日期数字 + 当天待办状态圆点（不显示文字条目，保持紧凑）"""

    clicked = pyqtSignal(str)  # 传出 yyyy-MM-dd

    def __init__(self, day_date, todos, is_today, is_selected, parent=None):
        super().__init__(parent)
        self.day_str = day_date.strftime("%Y-%m-%d")
        self.setObjectName("dayCell")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(40)
        self.setMaximumHeight(46)
        self.setCursor(Qt.PointingHandCursor)

        in_month = day_date.month == self._anchor_month()

        # 底色：选中 > 今天 > 非本月 > 普通
        if is_selected:
            bg, border = "#dbeafe", "#2563eb"
        elif is_today:
            bg, border = "#eff6ff", "#2563eb"
        elif not in_month:
            bg, border = "#f8fafc", "#e2e8f0"
        else:
            bg, border = "#ffffff", "#e2e8f0"

        self.setStyleSheet(
            f"QFrame#dayCell {{ background-color: {bg};"
            f" border: 1px solid {border}; border-radius: 6px; }}"
            f"QFrame#dayCell:hover {{ border: 1px solid #2563eb; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 3, 2, 3)
        lay.setSpacing(1)

        # 日期数字
        if is_selected:
            num_color = "#1d4ed8"
        elif is_today:
            num_color = "#2563eb"
        elif not in_month:
            num_color = "#cbd5e1"
        else:
            num_color = "#1e293b"
        lbl_num = QLabel(str(day_date.day))
        lbl_num.setAlignment(Qt.AlignCenter)
        lbl_num.setStyleSheet(
            f"font-size: 12px; font-weight: 500; color: {num_color};"
            " background: transparent; border: none;")
        lay.addWidget(lbl_num)

        # 状态圆点：优先显示最需要关注的（逾期 > 未完成 > 已完成）
        if todos:
            now = datetime.now()
            any_overdue = any(
                t.get("status") != "已完成" and t.get("deadline")
                and datetime.fromisoformat(t["deadline"]) < now
                for t in todos
                if t.get("deadline")
            )
            all_done = all(t.get("status") == "已完成" for t in todos)
            if any_overdue:
                dot_color = "#dc2626"  # 逾期红
            elif all_done:
                dot_color = "#16a34a"  # 完成绿
            else:
                dot_color = "#2563eb"  # 未完成蓝

            dots = QHBoxLayout()
            dots.setSpacing(2)
            dots.addStretch()
            for _ in range(min(len(todos), 3)):
                dot = QLabel()
                dot.setFixedSize(5, 5)
                dot.setStyleSheet(
                    f"background-color: {dot_color}; border-radius: 2px; border: none;")
                dots.addWidget(dot)
            dots.addStretch()
            lay.addLayout(dots)
        else:
            lay.addSpacing(5)

        lay.addStretch()

    def _anchor_month(self):
        return self.property("anchorMonth")

    def mousePressEvent(self, event):
        self.clicked.emit(self.day_str)
        super().mousePressEvent(event)


class TodoCalendar(QWidget):
    """月历侧栏：标题栏（月份 + 左右切换）+ 星期头 + 日期网格"""

    day_clicked = pyqtSignal(str)  # yyyy-MM-dd
    today_clicked = pyqtSignal()  # 点击「今天」：跳回当月并清除筛选

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.selected_day = ""  # 当前选中的日期 yyyy-MM-dd，空表示未选中
        today = date.today()
        self.display_year = today.year
        self.display_month = today.month
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # 标题栏：‹ 2026年9月 ›
        header = QHBoxLayout()
        header.setSpacing(4)
        self.btn_prev = QPushButton()
        self.btn_prev.setFixedSize(24, 24)
        self.btn_prev.setIcon(QIcon(svg_pixmap(ICON_CHEVRON_LEFT, 12, "#475569")))
        self.btn_prev.setIconSize(QSize(12, 12))
        self.btn_prev.setFlat(True)
        self.btn_prev.setToolTip("上一月")
        self.btn_prev.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 5px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        self.btn_prev.clicked.connect(self.prev_month)

        self.lbl_month = QLabel("")
        self.lbl_month.setStyleSheet("font-size: 14px; font-weight: 600; color: #1e293b;")
        header.addWidget(self.btn_prev)
        header.addWidget(self.lbl_month)
        header.addStretch()

        self.btn_today = QPushButton("今天")
        self.btn_today.setProperty("class", "btn-sm")
        self.btn_today.clicked.connect(self._on_today)
        header.addWidget(self.btn_today)

        self.btn_next = QPushButton()
        self.btn_next.setFixedSize(24, 24)
        self.btn_next.setIcon(QIcon(svg_pixmap(ICON_CHEVRON_RIGHT, 12, "#475569")))
        self.btn_next.setIconSize(QSize(12, 12))
        self.btn_next.setFlat(True)
        self.btn_next.setToolTip("下一月")
        self.btn_next.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 5px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        self.btn_next.clicked.connect(self.next_month)
        header.addWidget(self.btn_next)

        root.addLayout(header)

        # 星期头
        weekday_row = QGridLayout()
        weekday_row.setSpacing(3)
        for i, wd in enumerate(WEEKDAYS):
            lbl = QLabel(wd)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "font-size: 11px; color: #64748b; font-weight: 500; padding: 2px 0;")
            weekday_row.addWidget(lbl, 0, i)
        root.addLayout(weekday_row)

        # 日期网格
        self.grid = QGridLayout()
        self.grid.setSpacing(3)
        root.addLayout(self.grid, 1)

    def _on_today(self):
        """点击「今天」：展示月跳回当月、清除选中，并通知外部清列表筛选"""
        self.selected_day = ""
        self.go_today()
        self.today_clicked.emit()

    def go_today(self):
        today = date.today()
        self.display_year = today.year
        self.display_month = today.month
        self.refresh()

    def clear_selection(self):
        """清除选中，回到看全部待办"""
        self.selected_day = ""
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

    def select_day(self, day_str):
        """外部设置选中日期并跳到对应月"""
        self.selected_day = day_str
        try:
            d = datetime.fromisoformat(day_str)
            self.display_year = d.year
            self.display_month = d.month
        except Exception:
            pass
        self.refresh()

    def refresh(self):
        # 清空旧格子
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.lbl_month.setText(f"{self.display_year} 年 {self.display_month} 月")

        first = date(self.display_year, self.display_month, 1)
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
                cell = DayCell(
                    day, todos,
                    day_str == today_str,
                    day_str == self.selected_day,
                )
                cell.setProperty("anchorMonth", self.display_month)
                cell.clicked.connect(self._on_day_clicked)
                self.grid.addWidget(cell, row, col)

    def _on_day_clicked(self, day_str):
        """点击某天：设为选中，联动右侧列表筛选"""
        self.selected_day = day_str
        self.refresh()
        self.day_clicked.emit(day_str)
