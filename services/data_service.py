"""
数据服务
提供数据加载和访问的统一接口
"""

from typing import Dict, Optional
import pandas as pd
from core.data import CacheManager, CacheInvalidator
from core.data.base_loader import BaseLoader
from core.data.admission_loader import MultiYearAdmissionLoader
from core.data.school_loader import SchoolLoader
from core.data.subject_loader import SubjectLoader
from core.data.graduate_rate_loader import GraduateRateLoader
from utils.logger import get_logger


class DataService:
    """数据服务"""
    
    def __init__(self, cache_manager: CacheManager):
        """
        初始化数据服务
        
        Args:
            cache_manager: 缓存管理器
        """
        self.cache_manager = cache_manager
        self.cache_invalidator = CacheInvalidator(cache_manager)
        self.logger = get_logger("DataService")
        
        # 初始化加载器
        self.multi_year_loader = MultiYearAdmissionLoader(cache_manager)
        self.school_loader = None  # 懒加载
        self.subject_loader = None  # 懒加载
        self.graduate_rate_loader = None  # 懒加载
    
    def add_admission_data(self, year: int, file_path: str) -> None:
        """
        添加投档数据
        
        Args:
            year: 年份(2023/2024/2025)
            file_path: 数据文件路径
        """
        self.multi_year_loader.add_year(year, file_path)
        self.logger.info(f"添加投档数据: {year}")
    
    def load_admission_data(self, year: int, force_reload: bool = False) -> Optional[pd.DataFrame]:
        """
        加载指定年份的投档数据
        
        Args:
            year: 年份
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 数据
        """
        return self.multi_year_loader.load_year(year, force_reload)
    
    def load_all_admission_data(self, force_reload: bool = False) -> Dict[int, pd.DataFrame]:
        """
        加载所有年份数据
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            Dict[int, DataFrame]: 年份到数据的映射
        """
        return self.multi_year_loader.load_all_years(force_reload)
    
    def get_school_loader(self, file_path: str = "data/学校信息.md") -> SchoolLoader:
        """
        获取学校信息加载器(懒加载)
        
        Args:
            file_path: 学校信息文件路径
        
        Returns:
            SchoolLoader: 加载器实例
        """
        if self.school_loader is None:
            self.school_loader = SchoolLoader(self.cache_manager, file_path)
        return self.school_loader
    
    def load_school_info(self, force_reload: bool = False) -> pd.DataFrame:
        """
        加载学校信息
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 学校信息数据
        """
        loader = self.get_school_loader()
        return loader.load(force_reload)
    
    def get_subject_loader(self, file_path: str = "data/学科评估.md") -> SubjectLoader:
        """
        获取学科评估加载器(懒加载)
        
        Args:
            file_path: 学科评估文件路径
        
        Returns:
            SubjectLoader: 加载器实例
        """
        if self.subject_loader is None:
            self.subject_loader = SubjectLoader(self.cache_manager, file_path)
        return self.subject_loader
    
    def load_subject_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        加载学科评估数据
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 学科评估数据
        """
        loader = self.get_subject_loader()
        return loader.load(force_reload)
    
    def get_graduate_rate_loader(self, file_path: str = "data/高校保研率2025.md") -> GraduateRateLoader:
        """
        获取保研率加载器(懒加载)
        
        Args:
            file_path: 保研率文件路径
        
        Returns:
            GraduateRateLoader: 加载器实例
        """
        if self.graduate_rate_loader is None:
            self.graduate_rate_loader = GraduateRateLoader(self.cache_manager, file_path)
        return self.graduate_rate_loader
    
    def load_graduate_rate_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        加载保研率数据
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 保研率数据
        """
        loader = self.get_graduate_rate_loader()
        return loader.load(force_reload)
    
    def invalidate_caches(self, file_cache_mapping: Dict[str, str]) -> list:
        """
        失效相关缓存
        
        Args:
            file_cache_mapping: 文件路径到缓存键的映射
        
        Returns:
            被失效的缓存键列表
        """
        return self.cache_invalidator.check_all_data_files(file_cache_mapping)
    
    def clear_all_caches(self) -> None:
        """清空所有缓存"""
        self.cache_manager.clear()
        self.logger.info("清空所有缓存")
    
    def get_cache_stats(self) -> Dict[str, any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计信息字典
        """
        return self.cache_manager.get_stats()

    def get_data(self, year: int = 2025) -> pd.DataFrame:
        """
        获取数据（用于分析引擎）

        Args:
            year: 年份，默认2025（最新数据）

        Returns:
            DataFrame: 数据
        """
        df = self.load_admission_data(year)
        if df is None or df.empty:
            # 如果没有数据，返回空DataFrame并创建必要的列
            df = pd.DataFrame(columns=['招生院校', '招生专业', '投档最低分', '位次'])
            self.logger.warning(f"未找到{year}年数据，返回空DataFrame")
        return df

    def get_universities(self, year: int = 2025) -> pd.DataFrame:
        """
        获取院校聚合数据

        Args:
            year: 年份，默认2025（最新数据）

        Returns:
            DataFrame: 院校数据
        """
        df = self.get_data(year)

        if df.empty:
            return pd.DataFrame(columns=['院校名称', '最低分', '最高分', '平均分', '最低位次', '专业数量'])

        # 确定院校列名
        school_col = None
        if '招生院校' in df.columns:
            school_col = '招生院校'
        elif '院校名称' in df.columns:
            school_col = '院校名称'
        elif '学校名称' in df.columns:
            school_col = '学校名称'

        # 确定专业列名
        major_col = None
        if '招生专业' in df.columns:
            major_col = '招生专业'
        elif '专业名称' in df.columns:
            major_col = '专业名称'

        if not school_col or not major_col:
            return pd.DataFrame(columns=['院校名称', '最低分', '最高分', '平均分', '最低位次', '专业数量'])

        # 聚合院校数据
        agg_dict = {
            '投档最低分': ['min', 'max', 'mean'],
            major_col: 'count'
        }
        if '位次' in df.columns:
            agg_dict['位次'] = 'min'

        uni_groups = df.groupby(school_col).agg(agg_dict).reset_index()

        # 重命名列
        uni_groups.columns = ['院校名称', '最低分', '最高分', '平均分', '最低位次', '专业数量']

        return uni_groups.sort_values('平均分', ascending=False)

    def get_majors(self, year: int = 2025) -> pd.DataFrame:
        """
        获取专业聚合数据

        Args:
            year: 年份，默认2025（最新数据）

        Returns:
            DataFrame: 专业数据
        """
        df = self.get_data(year)

        if df.empty:
            return pd.DataFrame(columns=['专业名称', '最低分', '最高分', '平均分', '院校数量'])

        # 确定院校列名
        school_col = None
        if '招生院校' in df.columns:
            school_col = '招生院校'
        elif '院校名称' in df.columns:
            school_col = '院校名称'
        elif '学校名称' in df.columns:
            school_col = '学校名称'

        # 确定专业列名
        major_col = None
        if '招生专业' in df.columns:
            major_col = '招生专业'
        elif '专业名称' in df.columns:
            major_col = '专业名称'

        if not school_col or not major_col:
            return pd.DataFrame(columns=['专业名称', '最低分', '最高分', '平均分', '院校数量'])

        # 聚合专业数据
        major_groups = df.groupby(major_col).agg({
            '投档最低分': ['min', 'max', 'mean'],
            school_col: 'nunique'
        }).reset_index()

        # 重命名列
        major_groups.columns = ['专业名称', '最低分', '最高分', '平均分', '院校数量']
        return major_groups.sort_values('平均分', ascending=False)
