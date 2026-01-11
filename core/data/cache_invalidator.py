"""
缓存失效器模块
提供基于文件变化的自动缓存失效功能
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger


class CacheInvalidator:
    """缓存失效器"""
    
    def __init__(self, cache_manager, cache_dir: str = "cache"):
        """
        初始化缓存失效器
        
        Args:
            cache_manager: 缓存管理器实例
            cache_dir: 缓存目录
        """
        self.cache_manager = cache_manager
        self.cache_dir = Path(cache_dir)
        self.metadata_file = self.cache_dir / "file_timestamps.json"
        self.logger = get_logger("CacheInvalidator")
        self._load_timestamps()
    
    def _load_timestamps(self) -> None:
        """加载文件时间戳"""
        try:
            if self.metadata_file.exists():
                import json
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.timestamps = json.load(f)
            else:
                self.timestamps = {}
        except Exception as e:
            self.logger.warning(f"加载时间戳失败: {e}")
            self.timestamps = {}
    
    def _save_timestamps(self) -> None:
        """保存文件时间戳"""
        try:
            import json
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.timestamps, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"保存时间戳失败: {e}")
    
    def get_file_timestamp(self, filepath: str) -> Optional[float]:
        """
        获取文件时间戳
        
        Args:
            filepath: 文件路径
        
        Returns:
            文件时间戳,如果文件不存在则返回None
        """
        try:
            path = Path(filepath)
            if path.exists():
                return path.stat().st_mtime
            return None
        except Exception as e:
            self.logger.warning(f"获取文件时间戳失败: {e}")
            return None
    
    def has_file_changed(self, filepath: str) -> bool:
        """
        检查文件是否已更改
        
        Args:
            filepath: 文件路径
        
        Returns:
            文件是否已更改
        """
        current_timestamp = self.get_file_timestamp(filepath)
        if current_timestamp is None:
            return False
        
        stored_timestamp = self.timestamps.get(filepath)
        if stored_timestamp is None:
            # 首次检查
            self.timestamps[filepath] = current_timestamp
            self._save_timestamps()
            return True
        
        if current_timestamp > stored_timestamp:
            # 文件已更改
            self.timestamps[filepath] = current_timestamp
            self._save_timestamps()
            return True
        
        return False
    
    def check_and_invalidate(self, filepath: str, cache_key: str) -> bool:
        """
        检查文件变化并失效缓存
        
        Args:
            filepath: 要监控的文件路径
            cache_key: 关联的缓存键
        
        Returns:
            缓存是否被失效
        """
        if self.has_file_changed(filepath):
            self.logger.info(f"文件已更改,失效缓存: {filepath}")
            self.cache_manager.delete(cache_key)
            return True
        return False
    
    def check_all_data_files(self, file_cache_mapping: Dict[str, str]) -> List[str]:
        """
        检查所有数据文件并失效相关缓存
        
        Args:
            file_cache_mapping: 文件路径到缓存键的映射
        
        Returns:
            被失效的缓存键列表
        """
        invalidated_keys = []
        
        for filepath, cache_key in file_cache_mapping.items():
            if self.check_and_invalidate(filepath, cache_key):
                invalidated_keys.append(cache_key)
        
        if invalidated_keys:
            self.logger.info(f"失效的缓存: {', '.join(invalidated_keys)}")
        
        return invalidated_keys
