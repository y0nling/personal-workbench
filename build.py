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

    # 方案A（推荐）：onedir 文件夹分发，exe 只是启动器，无自解压
    cmd = [
        VENV_PYTHON, "-m", "PyInstaller",
        "--name=个人工作台",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--exclude-module=PyQt5.QtWebEngineCore",
        "--exclude-module=PyQt5.QtWebEngineWidgets",
        "--exclude-module=PyQt5.Qt3DAnimation",
        "--exclude-module=PyQt5.Qt3DCore",
        "--exclude-module=PyQt5.Qt3DExtras",
        "--exclude-module=PyQt5.Qt3DInput",
        "--exclude-module=PyQt5.Qt3DLogic",
        "--exclude-module=PyQt5.Qt3DRender",
        "--exclude-module=PyQt5.QtBluetooth",
        "--exclude-module=PyQt5.QtCharts",
        "--exclude-module=PyQt5.QtDataVisualization",
        "--exclude-module=PyQt5.QtDesigner",
        "--exclude-module=PyQt5.QtGamepad",
        "--exclude-module=PyQt5.QtHelp",
        "--exclude-module=PyQt5.QtLocation",
        "--exclude-module=PyQt5.QtMultimedia",
        "--exclude-module=PyQt5.QtMultimediaWidgets",
        "--exclude-module=PyQt5.QtNetworkAuth",
        "--exclude-module=PyQt5.QtNfc",
        "--exclude-module=PyQt5.QtPositioning",
        "--exclude-module=PyQt5.QtPurchasing",
        "--exclude-module=PyQt5.QtQuick",
        "--exclude-module=PyQt5.QtQuick3D",
        "--exclude-module=PyQt5.QtQuickWidgets",
        "--exclude-module=PyQt5.QtRemoteObjects",
        "--exclude-module=PyQt5.QtScript",
        "--exclude-module=PyQt5.QtScriptTools",
        "--exclude-module=PyQt5.QtScxml",
        "--exclude-module=PyQt5.QtSensors",
        "--exclude-module=PyQt5.QtSerialPort",
        "--exclude-module=PyQt5.QtSql",
        "--exclude-module=PyQt5.QtStateMachine",
        "--exclude-module=PyQt5.QtTest",
        "--exclude-module=PyQt5.QtTextToSpeech",
        "--exclude-module=PyQt5.QtUiTools",
        "--exclude-module=PyQt5.QtWebChannel",
        "--exclude-module=PyQt5.QtWebSockets",
        "--exclude-module=PyQt5.QtX11Extras",
        "--exclude-module=PyQt5.QtXml",
        "--exclude-module=PyQt5.QtXmlPatterns",
        "--hidden-import=openpyxl",
        "--hidden-import=config",
        "--hidden-import=models",
        "--hidden-import=utils.style",
        "--hidden-import=utils.settings",
        "--hidden-import=widgets.project_tab",
        "--hidden-import=widgets.todo_tab",
        "--hidden-import=widgets.summary_tab",
        "--hidden-import=widgets.people_tab",
        "--hidden-import=widgets.project_dialog",
        "--hidden-import=widgets.todo_dialog",
        "--hidden-import=widgets.export_xlsx_dialog",
        "--hidden-import=widgets.todo_calendar",
        "--hidden-import=widgets.personal_center",
        "--hidden-import=widgets.side_panel",
        "--hidden-import=widgets.tray_icon",
        "main.py",
    ]

    print("开始打包...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, shell=False)
    if result.returncode != 0:
        sys.exit(result.returncode)

    # 打包后清理：PyInstaller 会把已排除模块的部分 DLL 仍拷入，手动删除未用大件
    out_dir = os.path.join(here, "dist", "个人工作台", "_internal", "PyQt5", "Qt5")
    to_remove = [
        os.path.join(out_dir, "bin", "opengl32sw.dll"),      # GPU 软渲染回退（桌面 Qt 用不上）
        os.path.join(out_dir, "bin", "libGLESv2.dll"),
        os.path.join(out_dir, "bin", "d3dcompiler_47.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qicns.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qgif.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qtga.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qwbmp.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qwebp.dll"),
        os.path.join(out_dir, "plugins", "imageformats", "qtiff.dll"),
    ]
    for p in to_remove:
        if os.path.exists(p):
            os.remove(p)
            print(f"清理: {os.path.relpath(p, here)}")

    total = 0
    for root, _, files in os.walk(os.path.join(here, "dist", "个人工作台")):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    print(f"打包完成，总大小 {total / 1024 / 1024:.1f} MB -> dist/个人工作台/个人工作台.exe")
    sys.exit(0)


if __name__ == "__main__":
    main()
