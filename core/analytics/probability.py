"""
概率计算模块
提供录取概率计算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from utils.logger import get_logger


class ProbabilityCalculator:
    """概率计算器"""
    
    def __init__(self, data_processor):
        """
        初始化概率计算器
        
        Args:
            data_processor: 数据处理器
        """
        self.data_processor = data_processor
        self.logger = get_logger("ProbabilityCalculator")
    
    def calculate_probability(self, school_name: str, major_name: str, 
                             score: int, rank: Optional[int] = None) -> Dict[str, Any]:
        """
        计算录取概率
        
        Args:
            school_name: 学校名称
            major_name: 专业名称
            score: 考生分数
            rank: 考生位次
        
        Returns:
            概率计算结果
        """
        df = self.data_processor.get_data()
        
        # 筛选指定专业
        records = df[
            (df['招生院校'] == school_name) & 
            (df['招生专业'] == major_name)
        ]
        
        if len(records) == 0:
            return {
                'error': '未找到该专业',
                'school_name': school_name,
                'major_name': major_name
            }
        
        # 获取历史数据
        admission_score = records['投档最低分'].mean()
        admission_rank = records['位次'].mean()
        
        # 计算概率
        if rank is not None:
            # 基于位次计算
            if score > admission_score:
                probability = 0.95
            elif score >= admission_score - 10:
                probability = 0.70
            elif score >= admission_score - 20:
                probability = 0.50
            else:
                probability = 0.30
        else:
            # 基于分数计算
            if score > admission_score + 10:
                probability = 0.95
            elif score > admission_score:
                probability = 0.80
            elif score >= admission_score - 10:
                probability = 0.60
            elif score >= admission_score - 20:
                probability = 0.40
            else:
                probability = 0.20
        
        return {
            'school_name': school_name,
            'major_name': major_name,
            'student_score': score,
            'student_rank': rank,
            'admission_score': int(admission_score),
            'admission_rank': int(admission_rank) if not pd.isna(admission_rank) else None,
            'probability': float(f"{probability:.2f}"),
            'level': self._get_probability_level(probability)
        }
    
    def _get_probability_level(self, probability: float) -> str:
        """获取概率等级"""
        if probability >= 0.8:
            return "很高"
        elif probability >= 0.6:
            return "较高"
        elif probability >= 0.4:
            return "中等"
        elif probability >= 0.2:
            return "较低"
        else:
            return "很低"
    
    def batch_calculate(self, target_list: list, score: int, 
                       rank: Optional[int] = None) -> list:
        """
        批量计算概率
        
        Args:
            target_list: 目标列表 [{school_name, major_name}, ...]
            score: 考生分数
            rank: 考生位次
        
        Returns:
            概率结果列表
        """
        results = []
        for target in target_list:
            result = self.calculate_probability(
                target['school_name'],
                target['major_name'],
                score,
                rank
            )
            results.append(result)
        
        # 按概率排序
        results.sort(key=lambda x: x.get('probability', 0), reverse=True)
        
        return results
