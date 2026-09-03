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
from PyQt5.QtNetwork import QLocalSocket, QLocalServer

from config import APP_NAME
from models import WorkbenchData
from widgets.project_tab import ProjectTab
from widgets.todo_tab import TodoTab
from widgets.summary_tab import SummaryTab
from widgets.people_tab import PeopleTab
from widgets.personal_center import PersonalCenterTab
from widgets.login_dialog import LoginDialog
from widgets.tray_icon import TrayIcon
from utils.style import build_app_style
from utils.icons import app_icon
from utils.auth import AuthManager
from utils.settings import AppSettings


LOG_PATH = os.path.join(os.environ.get("TEMP", "."), "workbench_error.log")

# 单实例本地 socket 名
SINGLE_INSTANCE_KEY = "PersonalWorkbench_SingleInstance_y0nling"


def activate_existing_instance():
    """尝试连接已运行的实例并通知其激活窗口。成功返回 True，表示已有实例在运行。"""
    socket = QLocalSocket()
    socket.connectToServer(SINGLE_INSTANCE_KEY)
    if socket.waitForConnected(500):
        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        return True
    return False


class SingleInstanceServer(QLocalServer):
    """监听重复启动请求：收到连接时激活主窗口"""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.newConnection.connect(self._on_new_connection)

    def _on_new_connection(self):
        socket = self.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(300)
            socket.close()
            socket.deleteLater()
        # 激活已有窗口
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()


class MainWindow(QMainWindow):
    def __init__(self, data, settings, parent=None):
        super().__init__(parent)
        self.data = data
        self.settings = settings
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
        self.personal_tab = PersonalCenterTab(self.settings)

        self.tabs.addTab(self.project_tab, "项目看板")
        self.tabs.addTab(self.todo_tab, "待办事项")
        self.tabs.addTab(self.summary_tab, "周总结")
        self.tabs.addTab(self.people_tab, "人员管理")
        self.tabs.addTab(self.personal_tab, "个人中心")

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

        # ===== 单实例：重复启动时激活已有窗口后退出 =====
        if activate_existing_instance():
            sys.exit(0)

        # 移除残留的 socket（上次异常退出可能残留）
        QLocalServer.removeServer(SINGLE_INSTANCE_KEY)
        single_server = None  # 延后创建，等主窗口生成

        # ===== 应用设置与样式 =====
        settings = AppSettings()
        app.setStyleSheet(build_app_style(settings.font_scale))

        # ===== 登录 =====
        auth = AuthManager()
        login = LoginDialog(auth)
        if login.exec_() != QDialog.Accepted:
            sys.exit(0)

        data = WorkbenchData()

        window = MainWindow(data, settings)
        # 登录成功后把 auth 注入个人中心
        window.personal_tab.set_auth(auth)
        window.show()

        # 启动单实例监听
        single_server = SingleInstanceServer(window)
        single_server.listen(SINGLE_INSTANCE_KEY)

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
