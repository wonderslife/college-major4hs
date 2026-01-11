"""
宽表构建器
整合三年投档数据、学校信息、学科评估、保研率,生成综合大宽表
"""

import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from .base_loader import BaseLoader
from .admission_loader import MultiYearAdmissionLoader
from .school_loader import SchoolLoader
from .subject_loader import SubjectLoader
from .graduate_rate_loader import GraduateRateLoader
from core.models.admission_data import ComprehensiveRecord
from utils.logger import get_logger


class WideTableBuilder(BaseLoader):
    """宽表构建器"""
    
    def __init__(self, cache_manager):
        """
        初始化宽表构建器
        
        Args:
            cache_manager: 缓存管理器
        """
        super().__init__(cache_manager, "cache/wide_table_cache.pkl")
        self.logger = get_logger("WideTableBuilder")
    
    def _load_from_file(self) -> pd.DataFrame:
        """宽表不直接从文件加载"""
        return pd.DataFrame()
    
    def build_wide_table(self, 
                        multi_year_loader: MultiYearAdmissionLoader,
                        school_loader: Optional[SchoolLoader] = None,
                        subject_loader: Optional[SubjectLoader] = None,
                        graduate_rate_loader: Optional[GraduateRateLoader] = None,
                        force_rebuild: bool = False) -> pd.DataFrame:
        """
        构建综合大宽表
        
        Args:
            multi_year_loader: 多年份数据加载器
            school_loader: 学校信息加载器(可选)
            subject_loader: 学科评估加载器(可选)
            graduate_rate_loader: 保研率加载器(可选)
            force_rebuild: 是否强制重建
        
        Returns:
            DataFrame: 综合大宽表
        """
        # 检查缓存
        if not force_rebuild and self.cache_manager.exists(self._cache_key):
            cached_data = self.cache_manager.get(self._cache_key)
            if cached_data is not None:
                self.logger.info("从缓存加载宽表")
                return cached_data
        
        self.logger.info("开始构建综合大宽表")
        
        # Step 1: 加载三年投档数据
        df_2023 = multi_year_loader.load_year(2023)
        df_2024 = multi_year_loader.load_year(2024)
        df_2025 = multi_year_loader.load_year(2025)
        
        # Step 2: 重命名列
        df_2023 = df_2023.rename(columns={'score': 'score_2023', 'rank': 'rank_2023'})
        df_2024 = df_2024.rename(columns={'score': 'score_2024', 'rank': 'rank_2024'})
        df_2025 = df_2025.rename(columns={'score': 'score_2025', 'rank': 'rank_2025'})
        
        # Step 3: 提取关键字段
        key_cols_2023 = ['school_code', 'school_name', 'major_code', 'major_name', 'score_2023', 'rank_2023']
        key_cols_2024 = ['school_code', 'school_name', 'major_code', 'major_name', 'score_2024', 'rank_2024']
        key_cols_2025 = ['school_code', 'school_name', 'major_code', 'major_name', 'score_2025', 'rank_2025']
        
        df_2023 = df_2023[[col for col in key_cols_2023 if col in df_2023.columns]]
        df_2024 = df_2024[[col for col in key_cols_2024 if col in df_2024.columns]]
        df_2025 = df_2025[[col for col in key_cols_2025 if col in df_2025.columns]]
        
        # Step 4: 合并三年数据
        self.logger.info("合并三年投档数据")
        df = df_2025.merge(df_2024, on=['school_code', 'school_name', 'major_code', 'major_name'], how='outer')
        df = df.merge(df_2023, on=['school_code', 'school_name', 'major_code', 'major_name'], how='outer')
        
        # Step 5: 添加学校信息
        if school_loader:
            self.logger.info("添加学校信息")
            school_data = school_loader.load()
            if 'school_name' in school_data.columns:
                # 构建学校信息映射
                school_info_map = {}
                for _, row in school_data.iterrows():
                    school_name = row['学校名称']
                    school_info_map[school_name] = {
                        'province': self._extract_province(row.get('所在区域', '')),
                        'city': self._extract_city(row.get('所在区域', '')),
                        'authority': row.get('办学性质', ''),
                        'is_985': self._to_bool(row.get('985', '')),
                        'is_211': self._to_bool(row.get('985', '')) or self._to_bool(row.get('211', '')),
                        'is_double_first_class': self._to_bool(row.get('双一流', '')),
                        'is_private': self._to_bool(row.get('民办高校', '')),
                        'is_independent': self._to_bool(row.get('独立学院', ''))
                    }
                
                # 添加学校信息
                for col in ['province', 'city', 'authority', 'is_985', 'is_211', 
                           'is_double_first_class', 'is_private', 'is_independent']:
                    if col not in df.columns:
                        df[col] = None
                
                for idx, row in df.iterrows():
                    school_name = row['school_name']
                    if school_name in school_info_map:
                        info = school_info_map[school_name]
                        for col in ['province', 'city', 'authority']:
                            df.at[idx, col] = info[col]
                        for col in ['is_985', 'is_211', 'is_double_first_class', 'is_private', 'is_independent']:
                            df.at[idx, col] = info[col]
        
        # Step 6: 添加学科评估信息
        if subject_loader:
            self.logger.info("添加学科评估信息")
            if 'top_subject' not in df.columns:
                df['top_subject'] = None
            
            for idx, row in df.iterrows():
                school_name = row['school_name']
                top_subject = subject_loader.get_top_subject(school_name)
                if top_subject:
                    df.at[idx, 'top_subject'] = top_subject
        
        # Step 7: 添加保研率信息
        if graduate_rate_loader:
            self.logger.info("添加保研率信息")
            grad_cols = ['graduate_rate', 'graduate_rank', 'graduate_count', 'graduate_rank_change']
            for col in grad_cols:
                if col not in df.columns:
                    df[col] = None
            
            for idx, row in df.iterrows():
                school_name = row['school_name']
                grad_info = graduate_rate_loader.get_graduate_rate(school_name)
                if grad_info:
                    df.at[idx, 'graduate_rate'] = grad_info.get('graduate_rate')
                    df.at[idx, 'graduate_rank'] = grad_info.get('graduate_rank')
                    df.at[idx, 'graduate_count'] = grad_info.get('graduate_count')
                    df.at[idx, 'graduate_rank_change'] = grad_info.get('rank_change')
        
        # Step 8: 计算趋势分析字段
        self.logger.info("计算趋势分析字段")
        
        # 分数变化
        df['score_change'] = None
        df.loc[df['score_2023'].notna() & df['score_2025'].notna(), 'score_change'] = \
            df.loc[df['score_2023'].notna() & df['score_2025'].notna(), 'score_2025'] - \
            df.loc[df['score_2023'].notna() & df['score_2025'].notna(), 'score_2023']
        
        # 位次变化
        df['rank_change'] = None
        df.loc[df['rank_2023'].notna() & df['rank_2025'].notna(), 'rank_change'] = \
            df.loc[df['rank_2023'].notna() & df['rank_2025'].notna(), 'rank_2025'] - \
            df.loc[df['rank_2023'].notna() & df['rank_2025'].notna(), 'rank_2023']
        
        # 分数趋势
        df['score_trend'] = '未知'
        df.loc[df['score_change'] > 5, 'score_trend'] = '上升'
        df.loc[df['score_change'] < -5, 'score_trend'] = '下降'
        df.loc[(df['score_change'] >= -5) & (df['score_change'] <= 5) & (df['score_change'].notna()), 'score_trend'] = '稳定'
        
        # 是否有三年数据
        df['has_three_years'] = (
            df['score_2023'].notna() & 
            df['score_2024'].notna() & 
            df['score_2025'].notna()
        )
        
        # Step 9: 初始化缺失值
        for col in ['province', 'city', 'authority', 'top_subject']:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        for col in ['is_985', 'is_211', 'is_double_first_class', 'is_private', 'is_independent']:
            if col in df.columns:
                df[col] = df[col].fillna(False)
        
        # Step 10: 选择并排序列
        column_order = [
            'school_code', 'school_name', 'major_code', 'major_name',
            'province', 'city', 'authority',
            'is_985', 'is_211', 'is_double_first_class', 'is_private', 'is_independent',
            'graduate_rate', 'graduate_rank', 'graduate_count', 'graduate_rank_change',
            'top_subject',
            'score_2023', 'rank_2023',
            'score_2024', 'rank_2024',
            'score_2025', 'rank_2025',
            'score_trend', 'score_change', 'rank_change',
            'has_three_years'
        ]
        
        available_columns = [col for col in column_order if col in df.columns]
        df = df[available_columns]
        
        self.logger.info(f"宽表构建完成,共{len(df)}条记录")
        
        # 缓存宽表
        self.cache_manager.set(self._cache_key, df)
        
        return df
    
    def _extract_province(self, region: str) -> Optional[str]:
        """从区域字符串中提取省份"""
        if not region or pd.isna(region):
            return None
        parts = str(region).split()
        return parts[0] if parts else None
    
    def _extract_city(self, region: str) -> Optional[str]:
        """从区域字符串中提取城市"""
        if not region or pd.isna(region):
            return None
        parts = str(region).split()
        return parts[1] if len(parts) > 1 else None
    
    def _to_bool(self, value: any) -> bool:
        """转换为布尔值"""
        if pd.isna(value):
            return False
        return str(value).strip().upper() in ['Y', 'YES', 'TRUE', '是']
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据质量
        
        Args:
            df: 宽表数据
        
        Returns:
            数据质量报告
        """
        total_records = len(df)
        
        # 基础完整性
        has_school_code = df['school_code'].notna().sum()
        has_school_name = df['school_name'].notna().sum()
        has_major_name = df['major_name'].notna().sum()
        
        # 三年数据完整性
        has_2023 = df['score_2023'].notna().sum()
        has_2024 = df['score_2024'].notna().sum()
        has_2025 = df['score_2025'].notna().sum()
        has_three_years = df['has_three_years'].sum()
        
        # 学校信息覆盖率
        school_info_coverage = df['province'].notna().sum() / total_records * 100 if total_records > 0 else 0
        
        # 学科评估覆盖率
        subject_coverage = df['top_subject'].notna().sum() / total_records * 100 if total_records > 0 else 0
        
        # 保研率覆盖率
        graduate_coverage = df['graduate_rate'].notna().sum() / total_records * 100 if total_records > 0 else 0
        
        # 计算综合评分
        quality_scores = []
        quality_scores.append(min(has_school_code / total_records, 1.0) * 20)  # 院校编码完整性
        quality_scores.append(min(has_school_name / total_records, 1.0) * 20)  # 院校名称完整性
        quality_scores.append(min(has_2025 / total_records, 1.0) * 20)  # 2025数据完整性
        quality_scores.append(min(has_three_years / total_records, 1.0) * 15)  # 三年数据完整性
        quality_scores.append(min(school_info_coverage / 100, 1.0) * 10)  # 学校信息覆盖率
        quality_scores.append(min(subject_coverage / 100, 1.0) * 10)  # 学科评估覆盖率
        quality_scores.append(min(graduate_coverage / 100, 1.0) * 5)  # 保研率覆盖率
        
        total_score = sum(quality_scores)
        
        return {
            'total_records': total_records,
            'completeness': {
                'school_code': int(has_school_code),
                'school_name': int(has_school_name),
                'major_name': int(has_major_name),
                'has_2023': int(has_2023),
                'has_2024': int(has_2024),
                'has_2025': int(has_2025),
                'has_three_years': int(has_three_years)
            },
            'coverage': {
                'school_info': f'{school_info_coverage:.2f}%',
                'subject': f'{subject_coverage:.2f}%',
                'graduate': f'{graduate_coverage:.2f}%'
            },
            'quality_score': round(total_score, 2),
            'quality_level': '优秀' if total_score >= 85 else '良好' if total_score >= 70 else '一般' if total_score >= 60 else '较差'
        }
    
    def export_wide_table(self, df: pd.DataFrame, output_path: str = 'comprehensive_admission_table.csv') -> str:
        """
        导出宽表
        
        Args:
            df: 宽表数据
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"宽表已导出到: {output_file}")
        
        return str(output_file)
