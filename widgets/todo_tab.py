# -*- coding: utf-8 -*-
"""
待办事项模块 - 微软 To Do 风格
顶部快速输入（内容 + 人员 + 日期），圆点切换完成状态，已完成横线置灰
"""

from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QMessageBox, QDialog, QSplitter, QToolButton, QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QPen

from widgets.todo_dialog import TodoDialog
from widgets.todo_calendar import TodoCalendar
from utils.icons import svg_pixmap, ICON_PLUS, ICON_EDIT, ICON_DELETE


# 圆点图标（SVG），按状态着色
CIRCLE_TPL = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="{color}" stroke-width="2.2">'
    '<circle cx="12" cy="12" r="9"/></svg>'
)
CIRCLE_CHECK_TPL = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="{color}" stroke="{color}" stroke-width="2.2">'
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="M8 12.5l2.7 2.7L16.5 9" fill="none" stroke="#ffffff" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def circle_icon(done, overdue):
    """生成圆点图标：完成=实心绿勾，逾期未完成=红圈，普通未完成=蓝灰圈"""
    if done:
        return QIcon(svg_pixmap(CIRCLE_CHECK_TPL.format(color="#16a34a"), 22, "#16a34a"))
    color = "#dc2626" if overdue else "#2563eb"
    return QIcon(svg_pixmap(CIRCLE_TPL.format(color=color), 22, color))


class TodoRow(QWidget):
    """单条待办行：圆点 + 内容 + 元信息 + 操作按钮"""

    def __init__(self, todo, data, on_toggle, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.todo_id = todo["id"]
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        done = todo.get("status") == "已完成"

        # 逾期判断（仅未完成）
        overdue = False
        if not done and todo.get("deadline"):
            try:
                overdue = datetime.now() > datetime.fromisoformat(todo["deadline"])
            except Exception:
                pass

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        # 圆点按钮：切换完成/未完成
        self.btn_circle = QPushButton()
        self.btn_circle.setFixedSize(34, 34)
        self.btn_circle.setIcon(circle_icon(done, overdue))
        self.btn_circle.setIconSize(QSize(22, 22))
        self.btn_circle.setFlat(True)
        self.btn_circle.setCursor(Qt.PointingHandCursor)
        self.btn_circle.setToolTip("点击标记为已完成" if not done else "点击恢复为未完成")
        self.btn_circle.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 17px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        self.btn_circle.clicked.connect(lambda: self.on_toggle(self.todo_id))
        layout.addWidget(self.btn_circle, 0, Qt.AlignVCenter)

        # 中部：内容 + 元信息
        mid = QVBoxLayout()
        mid.setSpacing(2)

        self.lbl_content = QLabel(todo.get("content", ""))
        self.lbl_content.setWordWrap(True)
        content_style = "font-size: 14px;"
        if done:
            content_style += " color: #94a3b8; text-decoration: line-through;"
        elif overdue:
            content_style += " color: #dc2626;"
        else:
            content_style += " color: #1e293b;"
        self.lbl_content.setStyleSheet(content_style)
        mid.addWidget(self.lbl_content)

        metas = []
        owners = todo.get("owner") or []
        if owners:
            metas.append(f"👤 {'、'.join(owners)}")
        if todo.get("deadline"):
            dl_text = todo["deadline"].replace("T", " ")[:16]
            metas.append(("⏰ " if not overdue else "⚠️ 逾期 ") + dl_text)
        project_name = data.get_project_name(todo.get("projectId", ""))
        if project_name and project_name != "-":
            metas.append(f"📁 {project_name}")
        if metas:
            lbl_meta = QLabel("  ·  ".join(metas))
            lbl_meta.setStyleSheet("font-size: 12px; color: #64748b;")
            mid.addWidget(lbl_meta)
        layout.addLayout(mid, 1)

        # 右侧操作按钮
        btn_edit = QPushButton()
        btn_edit.setFixedSize(30, 30)
        btn_edit.setIcon(QIcon(svg_pixmap(ICON_EDIT, 14, "#2563eb")))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setFlat(True)
        btn_edit.setToolTip("编辑")
        btn_edit.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 6px; }"
            "QPushButton:hover { background-color: #eff6ff; }"
        )
        btn_edit.clicked.connect(lambda: self.on_edit(self.todo_id))

        btn_delete = QPushButton()
        btn_delete.setFixedSize(30, 30)
        btn_delete.setIcon(QIcon(svg_pixmap(ICON_DELETE, 14, "#dc2626")))
        btn_delete.setIconSize(QSize(14, 14))
        btn_delete.setFlat(True)
        btn_delete.setToolTip("删除")
        btn_delete.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 6px; }"
            "QPushButton:hover { background-color: #fef2f2; }"
        )
        btn_delete.clicked.connect(lambda: self.on_delete(self.todo_id))

        layout.addWidget(btn_edit, 0, Qt.AlignVCenter)
        layout.addWidget(btn_delete, 0, Qt.AlignVCenter)


class TodoTab(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # ===== 顶部快速输入栏（微软 To Do 风格）=====
        add_box = QFrame()
        add_box.setObjectName("todoAddBox")
        add_box.setStyleSheet(
            "QFrame#todoAddBox { background-color: #ffffff; border: 1px solid #cbd5e1;"
            " border-radius: 10px; }"
        )
        add_layout = QHBoxLayout(add_box)
        add_layout.setContentsMargins(12, 10, 12, 10)
        add_layout.setSpacing(10)

        self.input_content = QLineEdit()
        self.input_content.setPlaceholderText("添加待办：输入工作内容，回车快速创建…")
        self.input_content.setMinimumHeight(36)
        self.input_content.setStyleSheet(
            "QLineEdit { border: none; background: transparent; font-size: 15px; }"
            "QLineEdit:focus { border: none; }"
        )
        self.input_content.returnPressed.connect(self.quick_add)
        add_layout.addWidget(self.input_content, 1)

        self.combo_owner = QToolButton()
        self.combo_owner.setText("无负责人")
        self.combo_owner.setPopupMode(QToolButton.InstantPopup)
        self.combo_owner.setMinimumHeight(34)
        self.combo_owner.setMaximumWidth(150)
        self.combo_owner.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid #cbd5e1;"
            " border-radius: 6px; padding: 0 10px; }"
            "QToolButton:hover { border-color: #2563eb; }"
            "QMenu::item { padding: 6px 20px; }"
            "QMenu::item:selected { background-color: #dbeafe; }"
        )
        self.owner_menu = QMenu(self)
        self.combo_owner.setMenu(self.owner_menu)
        self._quick_owners = set()  # 快速添加时选中的负责人
        self.reload_owners()
        add_layout.addWidget(self.combo_owner)

        self.edit_deadline = QDateEdit()
        self.edit_deadline.setCalendarPopup(True)
        self.edit_deadline.setDisplayFormat("yyyy-MM-dd")
        self.edit_deadline.setDate(QDate.currentDate().addDays(1))
        self.edit_deadline.setSpecialValueText("无期限")
        self.edit_deadline.setMinimumHeight(34)
        self.edit_deadline.setStyleSheet("QDateEdit { background: transparent; }")
        add_layout.addWidget(self.edit_deadline)

        btn_quick = QPushButton(" 添加 ")
        btn_quick.setProperty("class", "primary")
        btn_quick.setMinimumHeight(34)
        btn_quick.setIcon(QIcon(svg_pixmap(ICON_PLUS, 14, "#ffffff")))
        btn_quick.clicked.connect(self.quick_add)
        add_layout.addWidget(btn_quick)

        root.addWidget(add_box)

        # ===== 筛选行 =====
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        filter_row.addWidget(QLabel("筛选："))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "未完成", "已完成"])
        self.filter_combo.currentTextChanged.connect(lambda _: self.refresh())
        filter_row.addWidget(self.filter_combo)
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 13px;")
        filter_row.addWidget(self.lbl_count)
        filter_row.addStretch()
        root.addLayout(filter_row)

        # ===== 待办列表（未完成在上、已完成置底置灰）=====
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; }")

        # 月历视图（上半部分）
        self.calendar = TodoCalendar(self.data)
        self.calendar.day_clicked.connect(self.on_calendar_day_clicked)

        # 上下分割：月历 / 待办列表
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.calendar)
        self.splitter.addWidget(self.scroll)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([320, 400])
        root.addWidget(self.splitter, 1)

    def reload_owners(self):
        """重新加载负责人多选菜单（人员变化后调用）"""
        self.owner_menu.clear()
        # 保留已勾选项（去掉已删除人员）
        self._quick_owners = {n for n in self._quick_owners if n in self.data.people}
        for person in self.data.people:
            act = QAction(person, self)
            act.setCheckable(True)
            act.setChecked(person in self._quick_owners)
            act.triggered.connect(lambda checked, name=person: self._toggle_quick_owner(name, checked))
            self.owner_menu.addAction(act)
        self._update_owner_button_text()

    def _toggle_quick_owner(self, name, checked):
        if checked:
            self._quick_owners.add(name)
        else:
            self._quick_owners.discard(name)
        self._update_owner_button_text()

    def _update_owner_button_text(self):
        if self._quick_owners:
            self.combo_owner.setText("、".join(sorted(self._quick_owners)))
        else:
            self.combo_owner.setText("无负责人")

    def quick_add(self):
        content = self.input_content.text().strip()
        if not content:
            QMessageBox.information(self, "提示", "请先输入待办内容")
            return
        owner = sorted(self._quick_owners)
        d = self.edit_deadline.date()
        deadline = d.toString("yyyy-MM-dd") if d.isValid() and not d.isNull() else ""
        self.data.add_todo(content, owner, deadline, "未完成", "")
        self.input_content.clear()
        self.refresh()

    def refresh(self):
        self.reload_owners()
        self.calendar.refresh()
        todos = self.data.sorted_todos()
        filt = self.filter_combo.currentText()

        undone = [t for t in todos if t.get("status") == "未完成"]
        done = [t for t in todos if t.get("status") == "已完成"]
        if filt == "未完成":
            shown = undone
        elif filt == "已完成":
            shown = done
        else:
            shown = undone + done

        self.lbl_count.setText(f"未完成 {len(undone)} 项 · 已完成 {len(done)} 项")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        if not shown:
            empty = QLabel("暂无待办，在上方输入框添加第一条吧")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #94a3b8; padding: 40px 0; font-size: 14px;")
            layout.addWidget(empty)
        else:
            prev_done = False
            for t in shown:
                is_done = t.get("status") == "已完成"
                # 未完成与已完成之间插入分隔线
                if not prev_done and is_done:
                    line = QFrame()
                    line.setFrameShape(QFrame.HLine)
                    line.setStyleSheet("color: #e2e8f0;")
                    layout.addWidget(line)
                    done_label = QLabel("已完成")
                    done_label.setStyleSheet(
                        "color: #16a34a; font-weight: 600; font-size: 13px; padding: 4px 6px;"
                    )
                    layout.addWidget(done_label)
                row = TodoRow(t, self.data, self.toggle_todo, self.edit_todo, self.delete_todo)
                layout.addWidget(row)
                prev_done = is_done

        layout.addStretch()
        self.scroll.setWidget(container)

    def on_calendar_day_clicked(self, day_str):
        """点击日历某天：在快速输入栏填入该日期，方便直接添加当天待办"""
        d = QDate.fromString(day_str, "yyyy-MM-dd")
        if d.isValid():
            self.edit_deadline.setDate(d)
            self.input_content.setFocus()

    def toggle_todo(self, todo_id):
        todo = next((t for t in self.data.todos if t["id"] == todo_id), None)
        if not todo:
            return
        new_status = "未完成" if todo.get("status") == "已完成" else "已完成"
        self.data.update_todo(todo_id, status=new_status)
        self.refresh()

    def edit_todo(self, todo_id):
        todo = next((t for t in self.data.todos if t["id"] == todo_id), None)
        if not todo:
            return
        dialog = TodoDialog(self.data, todo=todo, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            self.data.update_todo(todo_id, **d)
            self.refresh()

    def delete_todo(self, todo_id):
        reply = QMessageBox.question(
            self, "确认删除", "确定删除此待办吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.data.delete_todo(todo_id)
            self.refresh()
