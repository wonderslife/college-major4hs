"""
搜索模块
提供院校和专业搜索功能
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from utils.logger import get_logger


class SearchEngine:
    """搜索引擎"""
    
    def __init__(self, data_processor):
        """
        初始化搜索引擎
        
        Args:
            data_processor: 数据处理器
        """
        self.data_processor = data_processor
        self.logger = get_logger("SearchEngine")

    def _get_column_name(self, df, *candidates):
        """获取DataFrame中存在的列名（按优先级检查）"""
        for col in candidates:
            if col in df.columns:
                return col
        return None

    def _get_score_column(self, df):
        """获取分数列名"""
        return self._get_column_name(df, '投档最低分', '最低分')

    def _get_rank_column(self, df):
        """获取位次列名"""
        return self._get_column_name(df, '投档位次', '位次')

    def search_universities(self, keyword: str,
                           min_score: Optional[int] = None,
                           max_score: Optional[int] = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索院校

        Args:
            keyword: 搜索关键词
            min_score: 最低分数
            max_score: 最高分数
            limit: 返回数量

        Returns:
            搜索结果列表
        """
        try:
            df = self.data_processor.get_data()

            # 检查DataFrame是否为空
            if df.empty:
                return []

            # 确定院校列名
            school_col = self._get_column_name(df, '招生院校', '院校名称', '学校名称')
            if not school_col:
                return []

            # 确定专业列名
            major_col = self._get_column_name(df, '招生专业', '专业名称')
            if not major_col:
                return []

            # 确定分数和位次列名
            score_col = self._get_score_column(df)
            rank_col = self._get_rank_column(df)

            # 关键词过滤
            if keyword:
                df = df[df[school_col].str.contains(keyword, case=False, na=False)]

            # 分数过滤
            if score_col and min_score is not None:
                df = df[df[score_col] >= min_score]
            if score_col and max_score is not None:
                df = df[df[score_col] <= max_score]

            if df.empty:
                return []

            # 聚合院校
            agg_dict = {}
            if score_col:
                agg_dict[score_col] = ['min', 'max', 'mean']
            if rank_col:
                agg_dict[rank_col] = 'min'
            if major_col:
                agg_dict[major_col] = 'count'

            uni_groups = df.groupby(school_col).agg(agg_dict).reset_index()

            # 扁平化列名
            if rank_col:
                uni_groups.columns = ['院校名称', '最低分', '最高分', '平均分', '最低位次', '专业数量']
            else:
                uni_groups.columns = ['院校名称', '最低分', '最高分', '平均分', '专业数量']

            uni_groups = uni_groups.sort_values('平均分', ascending=False).head(limit)

            results = []
            for _, row in uni_groups.iterrows():
                result = {
                    'name': row['院校名称'],
                    'min_score': int(row['最低分']),
                    'max_score': int(row['最高分']),
                    'avg_score': float(f"{row['平均分']:.2f}"),
                    'major_count': int(row['专业数量'])
                }
                if rank_col and '最低位次' in row:
                    result['min_rank'] = int(row['最低位次'])
                else:
                    result['min_rank'] = 0
                results.append(result)

            return results
        except Exception as e:
            self.logger.error(f"搜索院校失败: {e}")
            return []
    
    def search_majors(self, keyword: str,
                     min_score: Optional[int] = None,
                     max_score: Optional[int] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索专业
        
        Args:
            keyword: 搜索关键词
            min_score: 最低分数
            max_score: 最高分数
            limit: 返回数量
        
        Returns:
            搜索结果列表
        """
        df = self.data_processor.get_data()

        # 检查DataFrame是否为空
        if df.empty:
            return []

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

        if not major_col or not school_col:
            return []

        # 关键词过滤
        if keyword:
            df = df[df[major_col].str.contains(keyword, case=False, na=False)]

        # 分数过滤
        score_col = None
        if '投档最低分' in df.columns:
            score_col = '投档最低分'
        elif '最低分' in df.columns:
            score_col = '最低分'

        if score_col and min_score is not None:
            df = df[df[score_col] >= min_score]
        if score_col and max_score is not None:
            df = df[df[score_col] <= max_score]

        if df.empty:
            return []

        # 聚合专业
        agg_dict = {}
        score_column = score_col if score_col else '投档最低分'
        if score_column in df.columns:
            agg_dict[score_column] = ['min', 'max', 'mean']
        if '位次' in df.columns:
            agg_dict['位次'] = ['min', 'mean']
        if school_col in df.columns:
            agg_dict[school_col] = 'nunique'
        major_groups = df.groupby(major_col).agg(agg_dict).reset_index()

        major_groups.columns = ['专业名称', '最低分', '最高分', '平均分', '最低位次', '平均位次', '开设院校数']
        major_groups = major_groups.sort_values('平均分', ascending=False).head(limit)
        
        return [
            {
                'name': row['专业名称'],
                'min_score': int(row['最低分']),
                'max_score': int(row['最高分']),
                'avg_score': float(f"{row['平均分']:.2f}"),
                'min_rank': int(row['最低位次']),
                'avg_rank': float(f"{row['平均位次']:.2f}"),
                'university_count': int(row['开设院校数'])
            }
            for _, row in major_groups.iterrows()
        ]
    
    def get_university_detail(self, name: str,
                            min_rank: Optional[int] = None,
                            max_rank: Optional[int] = None) -> Dict[str, Any]:
        """
        获取院校详情

        Args:
            name: 院校名称
            min_rank: 最低位次
            max_rank: 最高位次

        Returns:
            院校详情
        """
        df = self.data_processor.get_data()

        # 确定院校、专业、分数、位次列名
        school_col = self._get_column_name(df, '招生院校', '院校名称', '学校名称')
        major_col = self._get_column_name(df, '招生专业', '专业名称')
        score_col = self._get_score_column(df)
        rank_col = self._get_rank_column(df)

        if not school_col:
            return {'error': '数据缺少院校列'}

        # 筛选指定院校
        uni_data = df[df[school_col] == name]

        if len(uni_data) == 0:
            return {'error': '院校不存在'}

        # 应用位次筛选
        if min_rank is not None and rank_col:
            uni_data = uni_data[uni_data[rank_col] >= min_rank]
        if max_rank is not None and rank_col:
            uni_data = uni_data[uni_data[rank_col] <= max_rank]

        # 基础统计
        stats = {
            'name': name,
            'major_count': len(uni_data),
            'min_score': int(uni_data[score_col].min()) if score_col else 0,
            'max_score': int(uni_data[score_col].max()) if score_col else 0,
            'avg_score': float(f"{uni_data[score_col].mean():.2f}") if score_col else 0.0,
            'min_rank': int(uni_data[rank_col].min()) if rank_col else 0,
            'max_rank': int(uni_data[rank_col].max()) if rank_col else 0
        }

        # 专业列表
        majors = []
        for _, row in uni_data.iterrows():
            major_name = row[major_col] if major_col else '未知专业'
            majors.append({
                'name': major_name,
                'score': int(row[score_col]) if score_col else 0,
                'rank': int(row[rank_col]) if rank_col else 0
            })

        stats['majors'] = sorted(majors, key=lambda x: x['score'], reverse=True)

        return stats

    def get_major_detail(self, name: str,
                        min_rank: Optional[int] = None,
                        max_rank: Optional[int] = None) -> Dict[str, Any]:
        """
        获取专业详情

        Args:
            name: 专业名称
            min_rank: 最低位次
            max_rank: 最高位次

        Returns:
            专业详情
        """
        df = self.data_processor.get_data()

        # 确定院校、专业、分数、位次列名
        school_col = self._get_column_name(df, '招生院校', '院校名称', '学校名称')
        major_col = self._get_column_name(df, '招生专业', '专业名称')
        score_col = self._get_score_column(df)
        rank_col = self._get_rank_column(df)

        if not major_col or not school_col:
            return {'error': '数据缺少专业列或院校列'}

        # 筛选指定专业
        major_data = df[df[major_col] == name]

        if len(major_data) == 0:
            return {'error': '专业不存在'}

        # 应用位次筛选
        if min_rank is not None and rank_col:
            major_data = major_data[major_data[rank_col] >= min_rank]
        if max_rank is not None and rank_col:
            major_data = major_data[major_data[rank_col] <= max_rank]

        # 基础统计
        stats = {
            'name': name,
            'university_count': len(major_data),
            'min_score': int(major_data[score_col].min()) if score_col else 0,
            'max_score': int(major_data[score_col].max()) if score_col else 0,
            'avg_score': float(f"{major_data[score_col].mean():.2f}") if score_col else 0.0,
            'min_rank': int(major_data[rank_col].min()) if rank_col else 0,
            'max_rank': int(major_data[rank_col].max()) if rank_col else 0
        }

        # 院校列表
        universities = []
        for _, row in major_data.iterrows():
            uni_name = row[school_col] if school_col else '未知院校'
            universities.append({
                'university': uni_name,  # 前端期望的字段名
                'score': int(row[score_col]) if score_col else 0,
                'rank': int(row[rank_col]) if rank_col else 0,
                'city': '',  # 暂时为空，后续可以从学校信息中获取
                'detail_link': '',  # 暂时为空，后续可以从学校信息中获取
                'evaluations': [],  # 暂时为空，后续可以从学科评估中获取
                'postgraduate_info': None  # 暂时为空，后续可以从保研率中获取
            })

        # 为了兼容前端代码，将统计数据包装在 statistics 对象中
        return {
            'name': name,
            'statistics': {
                'total_universities': len(major_data),
                'min_score': int(major_data[score_col].min()) if score_col else 0,
                'max_score': int(major_data[score_col].max()) if score_col else 0,
                'avg_score': float(f"{major_data[score_col].mean():.2f}") if score_col else 0.0
            },
            'universities': sorted(universities, key=lambda x: x['score'], reverse=True)
        }

    def search_admissions(self, keyword: str = '',
                         min_score: Optional[int] = None,
                         max_score: Optional[int] = None,
                         min_rank: Optional[int] = None,
                         max_rank: Optional[int] = None,
                         city: Optional[str] = None,
                         is_985: Optional[bool] = None,
                         is_211: Optional[bool] = None,
                         is_double_first_class: Optional[bool] = None,
                         is_private: Optional[bool] = None,
                         is_independent: Optional[bool] = None,
                         sort_by: str = 'rank') -> List[Dict[str, Any]]:
        """
        搜索招生记录（返回详细记录）

        Args:
            keyword: 搜索关键词（院校名称或专业名称）
            min_score: 最低分数
            max_score: 最高分数
            min_rank: 最低位次
            max_rank: 最高位次
            city: 城市过滤
            is_985: 985院校过滤
            is_211: 211院校过滤
            is_double_first_class: 双一流院校过滤
            is_private: 民办院校过滤
            is_independent: 独立学院过滤
            sort_by: 排序字段（rank: 按位次升序, score_desc: 按分数降序）

        Returns:
            招生记录列表
        """
        try:
            df = self.data_processor.get_data()

            # 检查DataFrame是否为空
            if df.empty:
                return []

            # 确定院校、专业、分数、位次列名
            school_col = self._get_column_name(df, '招生院校', '院校名称', '学校名称')
            major_col = self._get_column_name(df, '招生专业', '专业名称')
            score_col = self._get_score_column(df)
            rank_col = self._get_rank_column(df)

            if not school_col or not major_col:
                return []

            # 关键词过滤
            if keyword:
                df = df[
                    df[school_col].str.contains(keyword, case=False, na=False) |
                    df[major_col].str.contains(keyword, case=False, na=False)
                ]

            # 分数过滤
            if score_col and min_score is not None:
                df = df[df[score_col] >= min_score]
            if score_col and max_score is not None:
                df = df[df[score_col] <= max_score]

            # 位次过滤
            if rank_col and min_rank is not None:
                df = df[df[rank_col] >= min_rank]
            if rank_col and max_rank is not None:
                df = df[df[rank_col] <= max_rank]

            # 转换为列表格式（先获取基本数据）
            results = []
            for _, row in df.iterrows():
                results.append({
                    'university': row[school_col],
                    'major': row[major_col],
                    'score': int(row[score_col]) if score_col else 0,
                    'rank': int(row[rank_col]) if rank_col else 0,
                    'city': '',
                    'tags': {},
                    'postgraduate_info': None,
                    'evaluations': [],
                    'detail_link': ''
                })

            # 加载学校信息并进行城市和标签过滤
            try:
                school_info_df = self.data_processor.get_school_loader().load()
                if school_info_df is not None and not school_info_df.empty:
                    # 确定学校信息列名
                    school_info_col = None
                    if '学校名称' in school_info_df.columns:
                        school_info_col = '学校名称'
                    elif '院校名称' in school_info_df.columns:
                        school_info_col = '院校名称'

                    if school_info_col:
                        # 创建学校信息映射
                        school_info_map = {}
                        for _, row in school_info_df.iterrows():
                            school_name = row[school_info_col]
                            school_info_map[school_name] = {
                                'city': row.get('所在城市', row.get('所在区域', '')),
                                'is_985': str(row.get('985', '')) == 'Y',
                                'is_211': '211' in str(row.get('办学层次', '')),
                                'is_double_first_class': str(row.get('双一流', '')) == 'Y',
                                'is_private': str(row.get('民办高校', '')) == 'Y',
                                'is_independent': str(row.get('独立学院', '')) == 'Y',
                                'detail_link': row.get('明细链接', '')
                            }

                        # 过滤和补充信息
                        filtered_results = []
                        for item in results:
                            uni_name = item['university']
                            if uni_name in school_info_map:
                                school_info = school_info_map[uni_name]

                                # 应用城市和标签过滤
                                passes_filter = True

                                # 城市过滤
                                if city and school_info['city'] != city:
                                    passes_filter = False

                                # 标签过滤
                                if is_985 is not None and school_info['is_985'] != is_985:
                                    passes_filter = False
                                if is_211 is not None and school_info['is_211'] != is_211:
                                    passes_filter = False
                                if is_double_first_class is not None and school_info['is_double_first_class'] != is_double_first_class:
                                    passes_filter = False
                                if is_private is not None and school_info['is_private'] != is_private:
                                    passes_filter = False
                                if is_independent is not None and school_info['is_independent'] != is_independent:
                                    passes_filter = False

                                if passes_filter:
                                    # 添加学校信息到结果
                                    item['city'] = school_info['city']
                                    item['tags'] = {
                                        'is_985': school_info['is_985'],
                                        'is_211': school_info['is_211'],
                                        'is_double_first_class': school_info['is_double_first_class'],
                                        'is_private': school_info['is_private'],
                                        'is_independent': school_info['is_independent']
                                    }
                                    item['detail_link'] = school_info['detail_link']
                                    filtered_results.append(item)

                        results = filtered_results
            except Exception as e:
                self.logger.warning(f"加载学校信息进行过滤失败: {e}")

            # 排序
            if sort_by == 'rank':
                results.sort(key=lambda x: x['rank'])  # 按位次升序
            elif sort_by == 'score_desc':
                results.sort(key=lambda x: x['score'], reverse=True)  # 按分数降序

            return results
        except Exception as e:
            self.logger.error(f"搜索招生记录失败: {e}")
            return []
