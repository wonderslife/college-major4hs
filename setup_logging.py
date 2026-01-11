"""
日志配置模块
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = 'app',
    log_dir: Optional[Path] = None,
    log_level: str = 'INFO',
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 10
) -> logging.Logger:
    """
    设置日志记录

    Args:
        name: 日志名称
        log_dir: 日志目录
        log_level: 日志级别
        max_bytes: 最大日志文件大小
        backup_count: 备份文件数量

    Returns:
        配置好的日志器
    """
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 清除现有处理器
    logger.handlers.clear()

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 确保日志目录存在
    if log_dir is None:
        log_dir = Path(__file__).parent / 'logs'

    log_dir.mkdir(exist_ok=True)

    # 文件处理器（滚动日志）
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / f'{name}.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 错误日志处理器
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / f'{name}_error.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 默认日志器
default_logger = setup_logging()
