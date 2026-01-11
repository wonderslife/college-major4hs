"""
基础数据加载器
定义数据加载器的通用接口和功能
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path
from utils.logger import get_logger


class BaseLoader(ABC):
    """数据加载器基类"""
    
    def __init__(self, cache_manager, file_path: str):
        """
        初始化加载器
        
        Args:
            cache_manager: 缓存管理器
            file_path: 数据文件路径
        """
        self.cache_manager = cache_manager
        self.file_path = Path(file_path)
        self._data: Optional[pd.DataFrame] = None
        self._cache_key = self._generate_cache_key()
        self.logger = get_logger(self.__class__.__name__)
    
    def _generate_cache_key(self) -> str:
        """生成缓存键"""
        return f"{self.__class__.__name__}_{self.file_path.name}"
    
    def load(self, force_reload: bool = False) -> pd.DataFrame:
        """
        加载数据
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 数据
        """
        # 检查缓存
        if not force_reload and self.cache_manager.exists(self._cache_key):
            cached_data = self.cache_manager.get(self._cache_key)
            if cached_data is not None:
                self.logger.info(f"从缓存加载数据: {self.file_path.name}")
                return cached_data
        
        # 从文件加载
        self.logger.info(f"从文件加载数据: {self.file_path.name}")
        data = self._load_from_file()
        
        # 数据清洗
        data = self._clean_data(data)
        
        # 缓存数据
        self.cache_manager.set(self._cache_key, data)
        
        return data
    
    @abstractmethod
    def _load_from_file(self) -> pd.DataFrame:
        """
        从文件加载数据(子类实现)
        
        Returns:
            DataFrame: 原始数据
        """
        pass
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗(可由子类重写)
        
        Args:
            df: 原始数据
        
        Returns:
            DataFrame: 清洗后的数据
        """
        return df
    
    def get_data(self) -> pd.DataFrame:
        """
        获取数据(使用缓存)
        
        Returns:
            DataFrame: 数据
        """
        return self.load()
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self.cache_manager.delete(self._cache_key)
        self._data = None
        self.logger.info(f"清除缓存: {self._cache_key}")
