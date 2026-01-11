"""
分析引擎
统一的分析接口,整合各个分析模块
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from .statistics import StatisticsAnalyzer
from .search import SearchEngine
from .probability import ProbabilityCalculator
from .recommendation import RecommendationEngine
from utils.logger import get_logger


class AnalyticsEngine:
    """数据分析引擎"""
    
    def __init__(self, data_processor):
        """
        初始化分析引擎
        
        Args:
            data_processor: 数据处理器
        """
        self.data_processor = data_processor
        self.logger = get_logger("AnalyticsEngine")
        
        # 初始化各个分析器
        self.statistics = StatisticsAnalyzer(data_processor)
        self.search = SearchEngine(data_processor)
        self.probability = ProbabilityCalculator(data_processor)
        self.recommendation = RecommendationEngine(data_processor)
    
    def get_basic_statistics(self, min_score: Optional[int] = None, 
                             max_score: Optional[int] = None,
                             min_rank: Optional[int] = None, 
                             max_rank: Optional[int] = None) -> Dict[str, Any]:
        """获取基础统计数据"""
        return self.statistics.get_basic_statistics(min_score, max_score, min_rank, max_rank)
    
    def get_score_distribution(self, min_score: Optional[int] = None,
                               max_score: Optional[int] = None,
                               min_rank: Optional[int] = None,
                               max_rank: Optional[int] = None) -> Dict[str, Any]:
        """获取分数分布"""
        return self.statistics.get_score_distribution(min_score, max_score, min_rank, max_rank)
    
    def get_rank_distribution(self, min_rank: Optional[int] = None,
                              max_rank: Optional[int] = None) -> Dict[str, Any]:
        """获取位次分布"""
        return self.statistics.get_rank_distribution(min_rank, max_rank)
    
    def get_top_universities(self, limit: int = 20,
                            min_score: Optional[int] = None,
                            max_score: Optional[int] = None,
                            school_info_df: Optional[pd.DataFrame] = None,
                            graduate_rate_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """获取热门院校排行"""
        return self.statistics.get_top_universities(limit, min_score, max_score, school_info_df, graduate_rate_df)
    
    def get_top_majors(self, limit: int = 20,
                      min_score: Optional[int] = None,
                      max_score: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取热门专业排行"""
        return self.statistics.get_top_majors(limit, min_score, max_score)
    
    def search_universities(self, keyword: str, 
                           min_score: Optional[int] = None,
                           max_score: Optional[int] = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """搜索院校"""
        return self.search.search_universities(keyword, min_score, max_score, limit)
    
    def search_majors(self, keyword: str,
                     min_score: Optional[int] = None,
                     max_score: Optional[int] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """搜索专业"""
        return self.search.search_majors(keyword, min_score, max_score, limit)
    
    def get_university_detail(self, name: str,
                            min_rank: Optional[int] = None,
                            max_rank: Optional[int] = None) -> Dict[str, Any]:
        """获取院校详情"""
        return self.search.get_university_detail(name, min_rank, max_rank)

    def get_major_detail(self, name: str,
                        min_rank: Optional[int] = None,
                        max_rank: Optional[int] = None) -> Dict[str, Any]:
        """获取专业详情"""
        return self.search.get_major_detail(name, min_rank, max_rank)
    
    def calculate_probability(self, school_name: str, major_name: str, 
                             score: int, rank: Optional[int] = None) -> Dict[str, Any]:
        """计算录取概率"""
        return self.probability.calculate_probability(school_name, major_name, score, rank)
    
    def batch_calculate_probability(self, target_list: list, score: int, 
                                    rank: Optional[int] = None) -> list:
        """批量计算概率"""
        return self.probability.batch_calculate(target_list, score, rank)
    
    def recommend_by_score(self, score: int, rank: Optional[int] = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """根据分数推荐"""
        return self.recommendation.recommend_by_score(score, rank, limit)
    
    def recommend_by_rank(self, rank: int, limit: int = 50) -> List[Dict[str, Any]]:
        """根据位次推荐"""
        return self.recommendation.recommend_by_rank(rank, limit)
    
    def smart_recommend(self, student_info: Dict[str, Any]) -> Dict[str, Any]:
        """智能推荐"""
        return self.recommendation.smart_recommend(student_info)
