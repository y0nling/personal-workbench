# -*- coding: utf-8 -*-
"""
数据模型与持久化模块
"""

import json
import os
import uuid
from datetime import datetime, timedelta

from config import DATA_VERSION, DEFAULT_DATA_DIR, DEFAULT_DATA_FILE, DEFAULT_PEOPLE


def now_str():
    """返回当前时间的 ISO 格式字符串"""
    return datetime.now().isoformat()


def short_datetime(iso_str):
    """将 ISO 时间字符串格式化为简短中文格式"""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str


def short_date(iso_str):
    """仅返回日期部分"""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_str


def get_week_range(now=None):
    """返回本周一 00:00 和本周日 23:59"""
    if now is None:
        now = datetime.now()
    weekday = now.weekday()  # 周一为 0
    monday = now - timedelta(days=weekday)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return monday, sunday


def is_in_this_week(iso_str):
    """判断某个时间是否在本周内"""
    if not iso_str:
        return False
    try:
        dt = datetime.fromisoformat(iso_str)
        monday, sunday = get_week_range()
        return monday <= dt <= sunday
    except Exception:
        return False


def generate_id():
    """生成唯一 ID"""
    return str(uuid.uuid4())


class WorkbenchData:
    """工作台数据容器"""

    def __init__(self, data_file=None):
        self.data_file = data_file or DEFAULT_DATA_FILE
        self.version = DATA_VERSION
        self.projects = []
        self.todos = []
        self.people = []
        self.load()

    def ensure_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load(self):
        """从 JSON 文件加载数据"""
        if not os.path.exists(self.data_file):
            self.people = list(DEFAULT_PEOPLE)
            self.save()
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.version = data.get("version", DATA_VERSION)
            self.projects = data.get("projects", [])
            self.todos = data.get("todos", [])
            self.people = data.get("people", list(DEFAULT_PEOPLE))
            self._migrate()
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.people = list(DEFAULT_PEOPLE)

    def _migrate(self):
        """数据结构迁移：owner 单值 -> 列表，项目补 members 字段"""
        for p in self.projects:
            if isinstance(p.get("owner"), str):
                p["owner"] = [p["owner"]] if p["owner"] else []
            if "members" not in p:
                p["members"] = []
        for t in self.todos:
            if isinstance(t.get("owner"), str):
                t["owner"] = [t["owner"]] if t["owner"] else []
        self.save()

    def save(self):
        """保存数据到 JSON 文件"""
        self.ensure_dir()
        data = {
            "version": self.version,
            "projects": self.projects,
            "todos": self.todos,
            "people": self.people,
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ===================== 项目操作 =====================
    def add_project(self, name, status, owner, members, start_date, deadline, pending, remark=""):
        project = {
            "id": generate_id(),
            "name": name,
            "status": status,
            "owner": owner,
            "members": members,
            "startDate": start_date,
            "deadline": deadline,
            "pending": pending,
            "remark": remark,
            "createdAt": now_str(),
            "updatedAt": now_str(),
        }
        self.projects.append(project)
        self.save()
        return project

    def update_project(self, project_id, **kwargs):
        for p in self.projects:
            if p["id"] == project_id:
                for key, value in kwargs.items():
                    if key in ("name", "status", "owner", "members", "startDate", "deadline", "pending", "remark"):
                        p[key] = value
                p["updatedAt"] = now_str()
                self.save()
                return p
        return None

    def delete_project(self, project_id):
        self.projects = [p for p in self.projects if p["id"] != project_id]
        # 清除待办关联
        for t in self.todos:
            if t.get("projectId") == project_id:
                t["projectId"] = ""
                t["updatedAt"] = now_str()
        self.save()

    def sorted_projects(self):
        """按创建时间倒序排列的项目列表"""
        return sorted(self.projects, key=lambda x: x.get("createdAt", ""), reverse=True)

    def get_project_name(self, project_id):
        for p in self.projects:
            if p["id"] == project_id:
                return p.get("name", "-")
        return "-"

    # ===================== 待办操作 =====================
    def add_todo(self, content, owner, deadline, status, project_id=""):
        todo = {
            "id": generate_id(),
            "content": content,
            "owner": owner,
            "deadline": deadline,
            "status": status,
            "projectId": project_id,
            "createdAt": now_str(),
            "updatedAt": now_str(),
        }
        self.todos.append(todo)
        self.save()
        return todo

    def update_todo(self, todo_id, **kwargs):
        for t in self.todos:
            if t["id"] == todo_id:
                for key, value in kwargs.items():
                    if key in ("content", "owner", "deadline", "status", "projectId"):
                        t[key] = value
                t["updatedAt"] = now_str()
                self.save()
                return t
        return None

    def delete_todo(self, todo_id):
        self.todos = [t for t in self.todos if t["id"] != todo_id]
        self.save()

    def sorted_todos(self):
        """未完成的排前面，再按截止时间升序"""
        def sort_key(t):
            s = 0 if t.get("status") == "未完成" else 1
            dl = t.get("deadline") or "9999-12-31"
            return (s, dl)
        return sorted(self.todos, key=sort_key)

    # ===================== 人员操作 =====================
    def add_person(self, name):
        name = name.strip()
        if not name:
            raise ValueError("姓名不能为空")
        if name in self.people:
            raise ValueError("该人员已存在")
        self.people.append(name)
        self.people.sort()
        self.save()

    def delete_person(self, name):
        if name in self.people:
            self.people.remove(name)
        # 同步清理项目和待办中已不存在的负责人
        for p in self.projects:
            if name in (p.get("owner") or []):
                p["owner"] = [x for x in p["owner"] if x != name]
                p["updatedAt"] = now_str()
            if name in (p.get("members") or []):
                p["members"] = [x for x in p["members"] if x != name]
                p["updatedAt"] = now_str()
        for t in self.todos:
            if name in (t.get("owner") or []):
                t["owner"] = [x for x in t["owner"] if x != name]
                t["updatedAt"] = now_str()
        self.save()

    # ===================== 周总结 =====================
    def weekly_summary(self):
        monday, sunday = get_week_range()
        completed = [p for p in self.projects if p.get("status") == "已完成" and is_in_this_week(p.get("updatedAt"))]
        in_progress = [p for p in self.projects if p.get("status") == "进行中"]
        pending = [p for p in self.projects if p.get("status") == "待协调" or (p.get("pending") and p.get("pending").strip())]
        week_todos = [t for t in self.todos if is_in_this_week(t.get("deadline")) or is_in_this_week(t.get("createdAt")) or is_in_this_week(t.get("updatedAt"))]
        done_todos = [t for t in week_todos if t.get("status") == "已完成"]
        undone_todos = [t for t in week_todos if t.get("status") == "未完成"]
        return {
            "week_start": monday.strftime("%Y-%m-%d"),
            "week_end": sunday.strftime("%Y-%m-%d"),
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "week_todos": week_todos,
            "done_todos": done_todos,
            "undone_todos": undone_todos,
        }

    # ===================== 导出导入 =====================
    def export_to_file(self, path):
        data = {
            "version": self.version,
            "projects": self.projects,
            "todos": self.todos,
            "people": self.people,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_from_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.version = data.get("version", DATA_VERSION)
        self.projects = data.get("projects", [])
        self.todos = data.get("todos", [])
        self.people = data.get("people", list(DEFAULT_PEOPLE))
        self.save()
