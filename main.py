# -*- coding: utf-8 -*-
"""
个人工作台 - PyQt5 桌面应用入口
"""

import sys
import os
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from config import APP_NAME
from models import WorkbenchData
from widgets.project_tab import ProjectTab
from widgets.todo_tab import TodoTab
from widgets.summary_tab import SummaryTab
from widgets.people_tab import PeopleTab
from widgets.tray_icon import TrayIcon
from utils.style import APP_STYLE
from utils.icons import app_icon


LOG_PATH = os.path.join(os.environ.get("TEMP", "."), "workbench_error.log")


class MainWindow(QMainWindow):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)
        self.center()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        self.project_tab = ProjectTab(self.data)
        self.todo_tab = TodoTab(self.data)
        self.summary_tab = SummaryTab(self.data)
        self.people_tab = PeopleTab(self.data)

        self.tabs.addTab(self.project_tab, "项目看板")
        self.tabs.addTab(self.todo_tab, "待办事项")
        self.tabs.addTab(self.summary_tab, "周总结")
        self.tabs.addTab(self.people_tab, "人员管理")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self._closing_to_tray = True

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def closeEvent(self, event):
        if self._closing_to_tray:
            event.ignore()
            self.hide()
        else:
            event.accept()

    def set_closing_to_tray(self, value):
        self._closing_to_tray = value


def show_error(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{__import__('datetime').datetime.now()}] {msg}\n")
    except Exception:
        pass


def main():
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setStyle("Fusion")
        app.setStyleSheet(APP_STYLE)

        data = WorkbenchData()

        window = MainWindow(data)
        window.show()

        tray = TrayIcon()
        tray.show_main.connect(window.show)
        tray.exit_app.connect(lambda: close_all(app, window, tray))
        tray.show()

        # 待办到期提醒定时器：每 30 秒检查一次
        reminder = ReminderChecker(data, tray, window)
        reminder.start()

        sys.exit(app.exec_())
    except Exception as e:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        QMessageBox.critical(None, "启动错误", f"程序启动失败，详情请查看:\n{LOG_PATH}\n\n{str(e)}")
        raise


class ReminderChecker:
    """待办到期提醒：提前 30 分钟气泡提醒，逾期持续提醒一次"""

    def __init__(self, data, tray, window):
        self.data = data
        self.tray = tray
        self.window = window
        self.notified = set()  # 已提醒过的待办 id + 触发时刻
        self.timer = QTimer()
        self.timer.setInterval(30 * 1000)  # 30 秒
        self.timer.timeout.connect(self.check)

    def start(self):
        self.check()
        self.timer.start()

    def check(self):
        from datetime import datetime, timedelta
        now = datetime.now()
        for t in self.data.todos:
            if t.get("status") != "未完成":
                continue
            dl_str = t.get("deadline", "")
            if not dl_str:
                continue
            try:
                dl = datetime.fromisoformat(dl_str)
            except Exception:
                continue
            content = t.get("content", "")
            # 提前 30 分钟提醒
            key = t["id"] + "@pre"
            if now <= dl and dl - now <= timedelta(minutes=30) and key not in self.notified:
                self.tray.showMessage(
                    "待办即将到期",
                    f"【{content}】\n截止：{dl.strftime('%H:%M')}，还有不到 30 分钟",
                    QIcon(), 5000
                )
                self.notified.add(key)
            # 已逾期提醒（同一待办每小时最多提醒一次）
            if dl < now:
                hour_key = t["id"] + "@overdue@" + now.strftime("%Y%m%d%H")
                if hour_key not in self.notified:
                    self.tray.showMessage(
                        "待办已逾期",
                        f"【{content}】\n已于 {dl.strftime('%m-%d %H:%M')} 到期，请尽快处理",
                        QIcon(), 5000
                    )
                    self.notified.add(hour_key)


def close_all(app, window, tray):
    window.set_closing_to_tray(False)
    tray.hide()
    window.close()
    app.quit()


if __name__ == "__main__":
    main()
