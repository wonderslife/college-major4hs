"""
装饰器工具模块
"""

import functools
import time
from typing import Callable, Any
from .logger import get_logger


def cache_result(ttl: int = 3600):
    """
    缓存结果装饰器
    
    Args:
        ttl: 缓存时间(秒)
    
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            key = f"{func.__name__}_{args}_{kwargs}"
            
            # 检查缓存
            if key in cache:
                cached_data, cached_time = cache[key]
                if time.time() - cached_time < ttl:
                    return cached_data
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache[key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    记录函数执行时间的装饰器
    
    Args:
        func: 要装饰的函数
    
    Returns:
        Callable: 装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__name__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"执行成功, 耗时: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"执行失败, 耗时: {execution_time:.2f}秒, 错误: {str(e)}")
            raise
    
    return wrapper
