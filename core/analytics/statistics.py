"""
统计分析模块
提供基础统计、分数分布、位次分布等功能
"""

import pandas as pd
from typing import Dict, Any, Optional
from utils.logger import get_logger


class StatisticsAnalyzer:
    """统计分析器"""
    
    def __init__(self, data_processor):
        """
        初始化统计分析器
        
        Args:
            data_processor: 数据处理器
        """
        self.data_processor = data_processor
        self.logger = get_logger("StatisticsAnalyzer")
    
    def get_basic_statistics(self, min_score: Optional[int] = None,
                             max_score: Optional[int] = None,
                             min_rank: Optional[int] = None,
                             max_rank: Optional[int] = None) -> Dict[str, Any]:
        """
        获取基础统计数据

        Args:
            min_score: 最低分数
            max_score: 最高分数
            min_rank: 最低位次
            max_rank: 最高位次

        Returns:
            统计数据字典
        """
        try:
            df = self.data_processor.get_data()

            # 检查DataFrame是否为空或缺少必需列
            if df.empty:
                self.logger.warning("DataFrame为空")
                return {
                    'total_records': 0,
                    'universities_count': 0,
                    'majors_count': 0,
                    'score_range': {
                        'min': 0,
                        'max': 0,
                        'mean': 0,
                        'median': 0
                    }
                }

            if '投档最低分' not in df.columns:
                self.logger.warning(f"DataFrame缺少'投档最低分'列，当前列: {df.columns.tolist()}")
                return {
                    'total_records': 0,
                    'universities_count': 0,
                    'majors_count': 0,
                    'score_range': {
                        'min': 0,
                        'max': 0,
                        'mean': 0,
                        'median': 0
                    }
                }

            self.logger.info(f"DataFrame列名: {df.columns.tolist()}, 数据行数: {len(df)}")

            # 应用筛选条件
            if min_score is not None:
                df = df[df['投档最低分'] >= min_score]
            if max_score is not None:
                df = df[df['投档最低分'] <= max_score]
            if min_rank is not None and '位次' in df.columns:
                df = df[df['位次'] >= min_rank]
            if max_rank is not None and '位次' in df.columns:
                df = df[df['位次'] <= max_rank]

            # 计算统计信息
            total_records = len(df)

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

            universities_count = df[school_col].nunique() if school_col else 0
            majors_count = df[major_col].nunique() if major_col else 0

            if total_records > 0:
                scores = df['投档最低分']
                min_score_val = int(scores.min())
                max_score_val = int(scores.max())
                mean_score = float(scores.mean())
                median_score = float(scores.median())

                score_range = {
                    'min': min_score_val,
                    'max': max_score_val,
                    'mean': mean_score,
                    'median': median_score
                }
            else:
                score_range = {
                    'min': 0,
                    'max': 0,
                    'mean': 0,
                    'median': 0
                }

            return {
                'total_records': total_records,
                'universities_count': universities_count,
                'majors_count': majors_count,
                'score_range': score_range
            }
        except Exception as e:
            self.logger.error(f"获取基础统计数据失败: {e}")
            return {
                'total_records': 0,
                'universities_count': 0,
                'majors_count': 0,
                'score_range': {
                    'min': 0,
                    'max': 0,
                    'mean': 0,
                    'median': 0
                },
                'error': str(e)
            }
    
    def get_score_distribution(self, min_score: Optional[int] = None,
                               max_score: Optional[int] = None,
                               min_rank: Optional[int] = None,
                               max_rank: Optional[int] = None) -> Dict[str, Any]:
        """
        获取分数分布

        Args:
            min_score: 最低分数
            max_score: 最高分数
            min_rank: 最低位次
            max_rank: 最高位次

        Returns:
            分数分布数据
        """
        try:
            df = self.data_processor.get_data()

            # 检查DataFrame是否为空或缺少必需列
            if df.empty or '投档最低分' not in df.columns:
                return {
                    'ranges': [{'min': 300 + i * 50, 'max': 349 + i * 50} for i in range(8)],
                    'scores': [0] * 8
                }

            # 应用分数筛选
            if min_score is not None:
                df = df[df['投档最低分'] >= min_score]
            if max_score is not None:
                df = df[df['投档最低分'] <= max_score]

            # 应用位次筛选
            if min_rank is not None and '位次' in df.columns:
                df = df[df['位次'] >= min_rank]
            if max_rank is not None and '位次' in df.columns:
                df = df[df['位次'] <= max_rank]

            if df.empty:
                return {
                    'ranges': [{'min': 300 + i * 50, 'max': 349 + i * 50} for i in range(8)],
                    'scores': [0] * 8
                }

            # 按50分分段
            bins = [300, 350, 400, 450, 500, 550, 600, 650, 700]
            labels = ['300-349', '350-399', '400-449', '450-499', '500-549', '550-599', '600-649', '650-700']

            df['分数段'] = pd.cut(df['投档最低分'], bins=bins, labels=labels, include_lowest=True)
            distribution = df['分数段'].value_counts().sort_index()

            return {
                'ranges': [{'min': 300 + i * 50, 'max': 349 + i * 50} for i in range(len(bins) - 1)],
                'scores': [int(val) for val in distribution.values]
            }
        except Exception as e:
            self.logger.error(f"获取分数分布失败: {e}")
            return {
                'ranges': [{'min': 300 + i * 50, 'max': 349 + i * 50} for i in range(8)],
                'scores': [0] * 8,
                'error': str(e)
            }
    
    def get_rank_distribution(self, min_rank: Optional[int] = None,
                              max_rank: Optional[int] = None) -> Dict[str, Any]:
        """
        获取位次分布

        Args:
            min_rank: 最低位次
            max_rank: 最高位次

        Returns:
            位次分布数据
        """
        try:
            df = self.data_processor.get_data()

            # 检查DataFrame是否为空或缺少必需列
            if df.empty or '位次' not in df.columns:
                bins = [0, 20000, 40000, 60000, 80000, 100000, 120000]
                return {
                    'ranges': [{'min': bins[i], 'max': bins[i + 1]} for i in range(len(bins) - 1)],
                    'counts': [0] * (len(bins) - 1)
                }

            # 应用位次筛选
            if min_rank is not None:
                df = df[df['位次'] >= min_rank]
            if max_rank is not None:
                df = df[df['位次'] <= max_rank]

            if df.empty:
                bins = [0, 20000, 40000, 60000, 80000, 100000, 120000]
                return {
                    'ranges': [{'min': bins[i], 'max': bins[i + 1]} for i in range(len(bins) - 1)],
                    'counts': [0] * (len(bins) - 1)
                }

            # 按20000位次分段
            bins = [0, 20000, 40000, 60000, 80000, 100000, 120000, float('inf')]
            labels = ['0-19999', '20000-39999', '40000-59999', '60000-79999', '80000-99999', '100000-119999', '120000+']

            df['位次段'] = pd.cut(df['位次'], bins=bins, labels=labels, include_lowest=True)
            distribution = df['位次段'].value_counts().sort_index()

            return {
                'ranges': [{'min': bins[i], 'max': bins[i + 1] if bins[i + 1] != float('inf') else 120000} for i in range(len(bins) - 1)],
                'counts': [int(val) for val in distribution.values]
            }
        except Exception as e:
            self.logger.error(f"获取位次分布失败: {e}")
            bins = [0, 20000, 40000, 60000, 80000, 100000, 120000]
            return {
                'ranges': [{'min': bins[i], 'max': bins[i + 1]} for i in range(len(bins) - 1)],
                'counts': [0] * (len(bins) - 1),
                'error': str(e)
            }
    
    def get_top_universities(self, limit: int = 20,
                            min_score: Optional[int] = None,
                            max_score: Optional[int] = None,
                            school_info_df: Optional[pd.DataFrame] = None,
                            graduate_rate_df: Optional[pd.DataFrame] = None) -> list:
        """
        获取热门院校排行(按平均分)

        Args:
            limit: 返回数量
            min_score: 最低分数
            max_score: 最高分数
            school_info_df: 学校信息DataFrame（可选）
            graduate_rate_df: 保研率DataFrame（可选）

        Returns:
            院校列表
        """
        try:
            unis = self.data_processor.get_universities().copy()

            if unis.empty:
                return []

            # 应用分数筛选
            if min_score is not None:
                unis = unis[unis['最低分'] >= min_score]
            if max_score is not None:
                unis = unis[unis['最高分'] <= max_score]

            unis = unis.head(limit)

            results = []
            for _, row in unis.iterrows():
                result = {
                    'name': row['院校名称'],
                    'min_score': int(row['最低分']),
                    'max_score': int(row['最高分']),
                    'avg_score': float(f"{row['平均分']:.2f}"),
                    'major_count': int(row['专业数量'])
                }
                if '最低位次' in row:
                    result['min_rank'] = int(row['最低位次'])
                else:
                    result['min_rank'] = 0

                # 添加学校信息（部门、城市等）
                if school_info_df is not None and not school_info_df.empty:
                    school_row = None
                    
                    # 尝试使用学校名称（因为这是学校信息中的列名）
                    if '学校名称' in school_info_df.columns:
                        school_row = school_info_df[school_info_df['学校名称'] == row['院校名称']]
                    
                    # 如果没找到，尝试使用院校名称
                    if school_row is None or school_row.empty:
                        if '院校名称' in school_info_df.columns:
                            school_row = school_info_df[school_info_df['院校名称'] == row['院校名称']]

                    if not school_row.empty:
                        school_data = school_row.iloc[0].to_dict()
                        result['department'] = school_data.get('主管部门', '')
                        # 优先使用所在城市，如果没有则使用所在区域
                        result['city'] = school_data.get('所在城市', school_data.get('所在区域', ''))
                        result['region'] = school_data.get('所在区域', '')
                        result['authority'] = school_data.get('主管部门', '')
                        result['level'] = school_data.get('办学层次', '')
                        result['is_double_first_class'] = school_data.get('双一流', '') == 'Y'
                        result['is_985'] = school_data.get('985', '') == 'Y'
                        result['is_211'] = school_data.get('211', '') == 'Y'
                        result['tags'] = {
                            'is_985': result['is_985'],
                            'is_211': result['is_211'],
                            'is_double_first_class': result['is_double_first_class']
                        }

                # 添加保研率信息
                if graduate_rate_df is not None and not graduate_rate_df.empty:
                    graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == row['院校名称']]
                    if not graduate_row.empty:
                        graduate_data = graduate_row.iloc[0].to_dict()
                        # 优先使用已经转换的 graduate_rate 列，如果没有则从原始列读取并转换
                        rate = graduate_data.get('graduate_rate', graduate_data.get('2025保研率', ''))
                        if rate and str(rate) != '':
                            # 如果是字符串且包含 %，先移除 % 符号
                            if isinstance(rate, str):
                                rate = rate.replace('%', '')
                            result['postgraduate_info'] = {
                                'rate': float(rate),
                                'count': int(graduate_data.get('graduate_count', graduate_data.get('2025保研人数', 0)))
                            }

                results.append(result)

            return results
        except Exception as e:
            self.logger.error(f"获取热门院校排行失败: {e}")
            return []
    
    def get_top_majors(self, limit: int = 20,
                      min_score: Optional[int] = None,
                      max_score: Optional[int] = None) -> list:
        """
        获取热门专业排行(按平均分)

        Args:
            limit: 返回数量
            min_score: 最低分数
            max_score: 最高分数

        Returns:
            专业列表
        """
        try:
            majors = self.data_processor.get_majors().copy()

            if majors.empty:
                return []

            # 应用分数筛选
            if min_score is not None:
                majors = majors[majors['最低分'] >= min_score]
            if max_score is not None:
                majors = majors[majors['最高分'] <= max_score]

            majors = majors.head(limit)

            return [
                {
                    'name': row['专业名称'],
                    'min_score': int(row['最低分']),
                    'max_score': int(row['最高分']),
                    'avg_score': float(f"{row['平均分']:.2f}"),
                    'university_count': int(row['院校数量'])
                }
                for _, row in majors.iterrows()
            ]
        except Exception as e:
            self.logger.error(f"获取热门专业排行失败: {e}")
            return []
