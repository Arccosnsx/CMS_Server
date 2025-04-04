import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """移除危险字符"""
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename.strip()

def prevent_path_traversal(base_path: str, user_path: str) -> Path:
    """防止路径穿越攻击"""
    full_path = (Path(base_path) / user_path).resolve()
    if not full_path.is_relative_to(Path(base_path).resolve()):
        raise ValueError("Invalid path")
    return full_path

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码的bcrypt哈希值"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)