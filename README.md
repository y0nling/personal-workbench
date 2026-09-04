# 个人工作台

基于 PyQt5 的个人桌面工作台，聚焦安全工作线的**待办管理**与**清单式项目管理**。

## 直接下载使用（推荐）

**无需安装 Python，下载解压即用。**

1. 打开 [Releases 页面](https://github.com/y0nling/personal-workbench/releases)
2. 下载最新版 `vX.X_个人工作台_便携版.zip`
3. 解压到任意目录（避免中文路径与空格）
4. 双击 `个人工作台.exe` 启动

> 首次启动会在 `C:\Users\<用户名>\Documents\PersonalWorkbench\` 自动生成空数据文件，**个人数据只存在本机，不会上传到 GitHub**。

---

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
- 单实例运行（重复启动只保留一个窗口）

## 数据存储

`C:\Users\<用户名>\Documents\PersonalWorkbench\workbench_data.json`

> 此文件为个人数据，**请勿上传到 GitHub**。如需备份，直接复制该 JSON 文件即可。

## 开发与打包

```bash
# 安装依赖
pip install PyQt5 openpyxl pyinstaller

# 本地运行
python main.py

# 打包（onedir 文件夹形式，exe 为启动器）
python build.py
```

打包产物输出到 `dist/个人工作台/` 文件夹，将整个文件夹压缩为 zip 后上传 Release。

## 技术栈

Python 3.13 · PyQt5 · openpyxl · PyInstaller
