# -*- coding: utf-8 -*-
"""
认证模块：账号密码验证与修改，凭据存储于 Documents/PersonalWorkbench/auth.json
"""

import json
import os
import hashlib

from config import DEFAULT_DATA_DIR

AUTH_FILE = os.path.join(DEFAULT_DATA_DIR, "auth.json")

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "123456"


def _hash(password, salt):
    """对密码加盐哈希"""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


class AuthManager:
    """登录认证管理器"""

    def __init__(self, auth_file=None):
        self.auth_file = auth_file or AUTH_FILE
        self.username = DEFAULT_USERNAME
        self._salt = ""
        self._password_hash = ""
        self._load()

    def _load(self):
        """加载凭据；文件不存在时写入默认账号 admin / 123456"""
        if not os.path.exists(self.auth_file):
            self._salt = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
            self._password_hash = _hash(DEFAULT_PASSWORD, self._salt)
            self._save()
            return
        try:
            with open(self.auth_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.username = data.get("username", DEFAULT_USERNAME)
            self._salt = data.get("salt", "")
            self._password_hash = data.get("password_hash", "")
        except Exception:
            # 凭据文件损坏时回退默认账号
            self.username = DEFAULT_USERNAME
            self._salt = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
            self._password_hash = _hash(DEFAULT_PASSWORD, self._salt)
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        with open(self.auth_file, "w", encoding="utf-8") as f:
            json.dump({
                "username": self.username,
                "salt": self._salt,
                "password_hash": self._password_hash,
            }, f, ensure_ascii=False, indent=2)

    def verify(self, username, password):
        """校验账号密码，返回是否通过"""
        if username != self.username:
            return False
        return _hash(password, self._salt) == self._password_hash

    def change_password(self, old_password, new_password):
        """修改密码：先校验旧密码，返回 (是否成功, 提示信息)"""
        if not self.verify(self.username, old_password):
            return False, "原密码不正确"
        if len(new_password) < 4:
            return False, "新密码长度至少 4 位"
        self._salt = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        self._password_hash = _hash(new_password, self._salt)
        self._save()
        return True, "密码修改成功"

    def reset_password(self):
        """恢复默认密码 123456"""
        self._salt = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        self._password_hash = _hash(DEFAULT_PASSWORD, self._salt)
        self._save()
