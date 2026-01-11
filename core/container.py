"""
依赖注入容器
管理所有核心组件的依赖关系
"""

from core.data import CacheManager, CacheInvalidator
from services.data_service import DataService
from services.app_service import AppService
from utils.logger import get_logger


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        """初始化容器"""
        self.logger = get_logger("DIContainer")
        
        # 单例组件
        self._cache_manager: CacheManager = None
        self._data_service: DataService = None
        self._app_service: AppService = None
    
    @property
    def cache_manager(self) -> CacheManager:
        """获取缓存管理器(单例)"""
        if self._cache_manager is None:
            self._cache_manager = CacheManager()
            self.logger.info("创建CacheManager实例")
        return self._cache_manager
    
    @property
    def data_service(self) -> DataService:
        """获取数据服务(单例)"""
        if self._data_service is None:
            self._data_service = DataService(self.cache_manager)
            self.logger.info("创建DataService实例")
        return self._data_service
    
    @property
    def app_service(self) -> AppService:
        """获取应用服务(单例)"""
        if self._app_service is None:
            self._app_service = AppService(self.data_service)
            self.logger.info("创建AppService实例")
        return self._app_service
    
    def clear_all(self) -> None:
        """清空所有单例"""
        self._cache_manager = None
        self._data_service = None
        self._app_service = None
        self.logger.info("清空所有单例")


# 全局容器实例
container = DIContainer()
