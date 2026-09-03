# 个人工作台

基于 PyQt5 的个人桌面工作台，聚焦安全工作线的**待办管理**与**清单式项目管理**。

## 功能模块

| 模块 | 说明 |
|---|---|
| 项目看板 | 表格清单：序号、项目名称、状态、负责人、截止日期、待协调事项、创建/更新时间；支持增删改、导出 Excel |
| 待办事项 | 微软 To Do 风格：顶部输入框直接写工作内容 + 绑定人员/日期，圆点切换完成状态，已完成横线置灰，到期前 30 分钟托盘气泡提醒 |
| 周总结 | 自动汇总本周完成/推进中/待协调事项，支持导出 TXT |
| 人员管理 | 维护负责人列表，供项目与待办下拉选择 |

## 桌面特性

- 系统托盘常驻，右键打开主窗口或退出
- 全局快捷键 `Ctrl+Shift+W` 呼出/隐藏主窗口
- 关闭按钮最小化到托盘，不退出程序
- 待办到期提醒（提前 30 分钟 + 逾期提醒）

## 数据存储

`C:\Users\<用户名>\Documents\PersonalWorkbench\workbench_data.json`

## 开发与打包

```bash
# 安装依赖
pip install PyQt5 openpyxl pyinstaller

# 本地运行
python main.py

# 打包 exe
python build.py
```

打包产物输出到 `dist/个人工作台.exe`（单文件）。

## 技术栈

Python 3.13 · PyQt5 · openpyxl · PyInstaller
