"""通用工具模块：JSON 配置读取、路径处理、文件操作"""
import json
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


def _read_json(filepath: Path) -> dict:
    """读取 JSON 文件并返回 dict"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_config(*keys: str):
    """
    读取 data/config.json 中的配置项
    用法：get_config("browser", "headless") -> False
    """
    config = _read_json(DATA_DIR / "config.json")
    for key in keys:
        config = config[key]
    return config


def get_account(*keys: str):
    """
    读取 data/account.json 中的账号数据
    用法：get_account("valid", "username") -> "15926689137"
    """
    account = _read_json(DATA_DIR / "account.json")
    for key in keys:
        account = account[key]
    return account
