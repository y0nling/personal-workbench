# -*- coding: utf-8 -*-
"""
个人工作台 - PyQt5 桌面应用入口
"""

import sys
import os
import traceback
import ctypes
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QDialog
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

# 单实例：Windows 命名互斥体（内核对象，进程被杀自动释放，绝无僵尸）
MUTEX_NAME = "Local\\PersonalWorkbench_Mutex_y0nling"
# 激活已有窗口的本地 socket 名
SINGLE_INSTANCE_KEY = "PersonalWorkbench_Activate_y0nling"

_kernel32 = ctypes.windll.kernel32 if sys.platform == "win32" else None


def is_first_instance():
    """判断是否为第一个实例。先 OpenMutex 探测是否已存在：
    - 能打开（已存在）→ 不是第一个实例，返回 False
    - 打不开 → 创建并占住互斥体，是第一个实例，返回 True
    命名互斥体是内核对象，进程被杀自动释放，绝无僵尸。"""
    if _kernel32 is None:
        return True  # 非 Windows 不做单实例限制
    # 先探测是否已有别的进程创建了互斥体
    existing = _kernel32.OpenMutexW(0x00100000, False, MUTEX_NAME)  # SYNCHRONIZE
    if existing:
        _kernel32.CloseHandle(existing)
        return False
    # 没有则创建占住
    _kernel32.CreateMutexW(None, True, MUTEX_NAME)
    return True


def activate_existing_instance():
    """已有实例在跑时，连它的本地 socket 通知激活窗口。返回是否成功通知。"""
    socket = QLocalSocket()
    socket.connectToServer(SINGLE_INSTANCE_KEY)
    if socket.waitForConnected(400):
        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(400)
        socket.disconnectFromServer()
        return True
    return False


def activate_existing_instance():
    """尝试连接已运行的实例并通知其激活窗口。
    成功返回 True，表示确有实例在运行；连接后无 ACK 视为残留 socket，返回 False。
    纯阻塞实现，不依赖 Qt 事件循环（本函数在事件循环启动前调用）。"""
    socket = QLocalSocket()
    socket.connectToServer(SINGLE_INSTANCE_KEY)
    if not socket.waitForConnected(500):
        socket.abort()
        return False
    socket.write(b"activate")
    socket.flush()
    socket.waitForBytesWritten(500)
    # 等待对方回 ACK。真实例在子线程里阻塞回 ACK；
    # 残留僵尸管道没人回，超时说明没有真实例。
    if socket.waitForReadyRead(800) and bytes(socket.readAll()) == b"ack":
        socket.disconnectFromServer()
        return True
    socket.abort()
    return False


class SingleInstanceServer(QLocalServer):
    """监听重复启动请求：收到连接时激活主窗口（真实例事件循环已跑，正常响应）"""

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

        # ===== 单实例：Windows 命名互斥体判断，重复启动时激活已有窗口后退出 =====
        if not is_first_instance():
            activate_existing_instance()
            sys.exit(0)

        # 第一个实例：清掉可能残留的激活 socket（上次异常退出遗留）
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
