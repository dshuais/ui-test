"""统一日志模块：按天分割日志文件，控制台+本地文件双输出"""
import logging
import sys
from datetime import datetime
from pathlib import Path

# 日志存放目录
LOG_DIR = Path(__file__).resolve().parent.parent / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_log_file_path() -> Path:
    """生成按日期命名的日志文件路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"ui_auto_{today}.log"


def setup_logger(name: str = "ui_auto") -> logging.Logger:
    """
    创建并返回 logger 实例
    - 控制台输出：INFO 及以上
    - 文件输出：DEBUG 及以上，按天切割
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 日志格式
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    # 文件 handler
    file_handler = logging.FileHandler(get_log_file_path(), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
