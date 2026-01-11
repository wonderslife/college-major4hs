"""
缓存管理器模块
提供统一的缓存管理功能
"""

import time
from typing import Any, Optional, Dict
from cachetools import TTLCache
from pathlib import Path
import json
from utils.logger import get_logger


class CacheManager:
    """统一的缓存管理器"""
    
    def __init__(self, ttl: int = 3600, maxsize: int = 100, cache_dir: str = "cache"):
        """
        初始化缓存管理器
        
        Args:
            ttl: 缓存存活时间(秒)
            maxsize: 最大缓存数量
            cache_dir: 缓存目录
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hit_count = 0
        self.miss_count = 0
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.logger = get_logger("CacheManager")
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """加载缓存元数据"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            self.logger.warning(f"加载缓存元数据失败: {e}")
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存缓存元数据失败: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
        
        Returns:
            缓存的数据，如果不存在则返回 None
        """
        if key in self.cache:
            self.hit_count += 1
            self.logger.debug(f"缓存命中: {key}")
            return self.cache[key]
        
        self.miss_count += 1
        self.logger.debug(f"缓存未命中: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间(秒),如果为None则使用默认TTL
        """
        self.cache[key] = value
        self.metadata[key] = {
            'created_at': time.time(),
            'ttl': ttl
        }
        self._save_metadata()
        self.logger.debug(f"设置缓存: {key}")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存数据
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if key in self.cache:
            del self.cache[key]
            if key in self.metadata:
                del self.metadata[key]
                self._save_metadata()
            self.logger.debug(f"删除缓存: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        self.metadata.clear()
        self._save_metadata()
        self.logger.info("清空所有缓存")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': f'{hit_rate:.2f}%',
            'cache_size': len(self.cache)
        }
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            缓存是否存在
        """
        return key in self.cache
