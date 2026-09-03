# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
"""

import os
import sys
import subprocess

VENV_PYTHON = r"C:\Users\y0nling\.workbuddy\binaries\python\envs\default\Scripts\python.exe"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    cmd = [
        VENV_PYTHON, "-m", "PyInstaller",
        "--name=个人工作台",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--hidden-import=PyQt5.sip",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=openpyxl",
        "--hidden-import=config",
        "--hidden-import=models",
        "--hidden-import=utils.style",
        "--hidden-import=widgets.project_tab",
        "--hidden-import=widgets.todo_tab",
        "--hidden-import=widgets.summary_tab",
        "--hidden-import=widgets.people_tab",
        "--hidden-import=widgets.project_dialog",
        "--hidden-import=widgets.todo_dialog",
        "--hidden-import=widgets.export_xlsx_dialog",
        "--hidden-import=widgets.todo_calendar",
        "--hidden-import=widgets.login_dialog",
        "--hidden-import=widgets.personal_center",
        "--hidden-import=utils.auth",
        "--hidden-import=utils.settings",
        "--hidden-import=widgets.side_panel",
        "--hidden-import=widgets.tray_icon",
        "--collect-all", "PyQt5",
        "main.py",
    ]

    print("开始打包...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, shell=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
