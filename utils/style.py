# -*- coding: utf-8 -*-
"""
全局 QSS 样式：科技蓝主调 + 红色强调
"""

APP_STYLE = """
/* ===================== 基础与主窗口 ===================== */
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", "SimHei", sans-serif;
    font-size: 14px;
    color: #1e293b;
    outline: none;
}

/* ===================== 标签页 ===================== */
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    border-radius: 0 10px 10px 10px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 12px 28px;
    margin-right: 6px;
    margin-bottom: -1px;
    color: #475569;
    font-weight: 500;
    font-size: 14px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
}

QTabBar::tab:hover:!selected {
    background-color: #dbeafe;
    color: #2563eb;
}

/* ===================== 按钮 ===================== */
QPushButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 16px;
    min-height: 30px;
    font-weight: 500;
}

QPushButton:hover {
    border-color: #2563eb;
    color: #2563eb;
    background-color: #eff6ff;
}

QPushButton:pressed {
    background-color: #dbeafe;
}

QPushButton.primary,
QPushButton[class="primary"] {
    background-color: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
    font-weight: 600;
}

QPushButton.primary:hover,
QPushButton[class="primary"]:hover {
    background-color: #1d4ed8;
    border-color: #1d4ed8;
    color: #ffffff;
}

QPushButton.danger,
QPushButton[class="danger"] {
    color: #dc2626;
    border-color: #dc2626;
    background-color: #ffffff;
}

QPushButton.danger:hover,
QPushButton[class="danger"]:hover {
    background-color: #dc2626;
    color: #ffffff;
}

QPushButton[class="btn-sm"] {
    padding: 4px 10px;
    font-size: 13px;
    min-height: 24px;
}

/* ===================== 输入框 ===================== */
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 10px;
    background-color: #ffffff;
    color: #1e293b;
    min-height: 24px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border-color: #2563eb;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #94a3b8;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    width: 0px;
    height: 0px;
}

QComboBox QAbstractItemView {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background-color: #ffffff;
    selection-background-color: #dbeafe;
    selection-color: #1e293b;
}

/* ===================== 表格 ===================== */
QTableWidget {
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    background-color: #ffffff;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    selection-color: #1e293b;
    alternate-background-color: #f8fafc;
}

QTableWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #e2e8f0;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #1e40af;
    font-weight: 600;
    padding: 12px 14px;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    border-right: 1px solid #e2e8f0;
}

QHeaderView::section:last {
    border-right: none;
}

/* ===================== 滚动条 ===================== */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f1f5f9;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ===================== 对话框与分组 ===================== */
QDialog {
    background-color: #f8fafc;
}

QGroupBox {
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 14px;
    padding-bottom: 14px;
    font-weight: 600;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: #1e40af;
    font-size: 15px;
}

QLabel {
    color: #334155;
}

QLabel[class="label-secondary"] {
    color: #64748b;
    font-size: 13px;
}

/* ===================== 消息框 ===================== */
QMessageBox {
    background-color: #f8fafc;
}

QMessageBox QPushButton {
    min-width: 70px;
}

/* ===================== 菜单 ===================== */
QMenu {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 6px 0;
}

/* ===================== 工具提示 ===================== */
QToolTip {
    background-color: #1e293b;
    color: #f8fafc;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
