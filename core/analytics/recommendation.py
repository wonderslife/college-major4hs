"""
推荐引擎模块
提供基于排名顺序的志愿推荐功能
完全忽略分数差异，仅基于学生位次与专业录取位次的相对比较

院校推荐规则说明：
===================

1. 保底院校规则：
   - 录取位次范围：学生当前位次 至 (学生位次 + 100)
   - 逻辑：学校录取位次 > 学生位次，学生排名更靠前，有录取优势
   - 示例：位次5000的学生，推荐5000-5100位次的学校
   - 用途：确保至少有一定数量的保底选择，提高录取安全性

2. 匹配院校规则（稳健/稳妥）：
   - 录取位次范围：(学生位次 - 100) 至 (学生位次 + 100)
   - 逻辑：学校录取位次与学生位次相当，录取概率较高
   - 示例：位次5000的学生，推荐4900-5100位次的学校
   - 用途：主要志愿部分，录取概率在50%-80%之间

3. 冲刺院校规则：
   - 录取位次范围：(学生位次 - 200) 至 学生位次
   - 逻辑：学校录取位次 < 学生位次，学生排名靠后，录取有难度
   - 示例：位次5000的学生，推荐4800-5000位次的学校
   - 用途：尝试冲击更好的学校，但风险可控

总体策略说明：
- 位次范围限制：只推荐在合理位次范围内的学校，避免推荐不切实际的目标
- 筛选条件：支持按地区、专业、学校类型（985/211/双一流）筛选
- 动态调整：根据实际可用的学校数量，自动调整各策略的推荐数量
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from utils.logger import get_logger


class PureRankRecommender:
    """纯基于排名的推荐器"""
    
    def __init__(self, items):
        """
        初始化排名推荐器
        
        Args:
            items: 候选项目列表，每个项目包含rank字段
        """
        self.items = items
        self.sorted_items = self._preprocess()
    
    def _preprocess(self):
        """预处理：按排名排序并建立索引"""
        return sorted(self.items, key=lambda x: x['rank'])
    
    def recommend(self, user_rank, strategy="balanced", top_k=120):
        """
        基于排名推荐
        
        Args:
            user_rank: 学生位次（数值越小竞争力越强）
            strategy: 推荐策略 balanced(平衡), conservative(保守), aggressive(激进)
            top_k: 返回推荐数量
        
        Returns:
            推荐列表
        """
        if strategy == "conservative":
            return self._conservative_recommend(user_rank, top_k)
        elif strategy == "aggressive":
            return self._aggressive_recommend(user_rank, top_k)
        else:
            return self._balanced_recommend(user_rank, top_k)
    
    def _balanced_recommend(self, user_rank, top_k=120, safe_ratio=0.6):
        """平衡策略：保底+冲刺混合
        
        逻辑说明：
        - 保底院校：录取位次在学生位次至(学生位次+100)之间
        - 冲刺院校：录取位次在(学生位次-200)至学生位次之间
        
        位次范围限制：
        - 保底院校：录取位次在学生位次到学生位次+100之间（确保可行性）
        - 冲刺院校：录取位次在学生位次-200到学生位次之间（适当放宽冲刺范围）
        """
        safe_count = int(top_k * safe_ratio)
        challenge_count = top_k - safe_count
        
        # 设置位次范围限制
        safe_min_rank = user_rank
        safe_max_rank = user_rank + 100  # 保底上限：学生位次+100
        challenge_min_rank = user_rank - 200  # 冲刺下限：学生位次-200
        challenge_max_rank = user_rank
        
        # 保底：录取位次 > 学生位次（学生排名更靠前，更容易录取）
        safe_items = []
        for item in self.sorted_items:
            if item['rank'] > user_rank and item['rank'] <= safe_max_rank:  # 保底：学生有优势，且在合理范围内
                item_copy = item.copy()
                item_copy['category'] = '保底'
                item_copy['advantage'] = user_rank - item['rank']  # 正数表示优势
                safe_items.append(item_copy)
                if len(safe_items) >= safe_count:
                    break
        
        # 冲刺：录取位次 <= 学生位次（学生排名更靠后，更难录取）
        challenge_items = []
        for item in reversed(self.sorted_items):  # 从最难的开始
            if item['rank'] <= user_rank and item['rank'] >= challenge_min_rank:  # 冲刺：学生有劣势，但差距不太大
                item_copy = item.copy()
                item_copy['category'] = '冲刺'
                item_copy['advantage'] = user_rank - item['rank']  # 负数表示劣势
                challenge_items.append(item_copy)
                if len(challenge_items) >= challenge_count:
                    break
        
        # 如果safe_items不足，用challenge_items补足
        if len(safe_items) < safe_count:
            remaining = safe_count - len(safe_items)
            for item in challenge_items[:remaining]:
                if len(safe_items) >= safe_count:
                    break
                item_copy = item.copy()
                item_copy['category'] = '保底'
                safe_items.append(item_copy)
        
        # 如果challenge_items不足，用safe_items补足
        if len(challenge_items) < challenge_count:
            remaining = challenge_count - len(challenge_items)
            for item in safe_items[-remaining:]:
                if len(challenge_items) >= challenge_count:
                    break
                item_copy = item.copy()
                item_copy['category'] = '冲刺'
                challenge_items.append(item_copy)
        
        # 合并结果：保底在前，冲刺在后
        return safe_items + challenge_items
    
    def _conservative_recommend(self, user_rank, top_k=120):
        """保守策略：主要推荐保底院校
        
        录取位次 > 学生位次：对学生来说是保底
        
        位次范围限制：
        - 保底院校：录取位次在学生位次到学生位次+100之间
        - 示例：位次5000的学生，推荐5000-5100位次的学校
        """
        safe_min_rank = user_rank
        safe_max_rank = user_rank + 100  # 保底上限：学生位次+100
        
        safe_items = []
        for item in self.sorted_items:
            if item['rank'] > user_rank and item['rank'] <= safe_max_rank:  # 保底且在合理范围内
                item_copy = item.copy()
                item_copy['category'] = '保底'
                item_copy['advantage'] = user_rank - item['rank']
                safe_items.append(item_copy)
                if len(safe_items) >= top_k:
                    break
        
        # 如果保底院校不足，用其他院校补足
        if len(safe_items) < top_k:
            remaining = top_k - len(safe_items)
            for item in self.sorted_items:
                if len(safe_items) >= top_k:
                    break
                if item['rank'] <= user_rank:  # 原本不符合条件的现在也加入
                    item_copy = item.copy()
                    item_copy['category'] = '保底'
                    item_copy['advantage'] = user_rank - item['rank']
                    safe_items.append(item_copy)
        
        return safe_items
    
    def _aggressive_recommend(self, user_rank, top_k=120):
        """激进策略：主要推荐冲刺院校
        
        录取位次 <= 学生位次：对学生来说是冲刺
        
        位次范围限制：
        - 冲刺院校：录取位次在学生位次-200到学生位次之间
        - 示例：位次5000的学生，推荐4800-5000位次的学校
        """
        challenge_min_rank = user_rank - 200  # 冲刺下限：学生位次-200
        challenge_max_rank = user_rank
        
        challenge_items = []
        # 从最接近学生位次的开始，向上取冲刺院校
        for item in self.sorted_items:
            if item['rank'] <= user_rank and item['rank'] >= challenge_min_rank:  # 冲刺且在合理范围内
                item_copy = item.copy()
                item_copy['category'] = '冲刺'
                item_copy['advantage'] = user_rank - item['rank']
                challenge_items.append(item_copy)
                if len(challenge_items) >= top_k:
                    break
        
        # 如果冲刺院校不足，用其他院校补足
        if len(challenge_items) < top_k:
            remaining = top_k - len(challenge_items)
            for item in reversed(self.sorted_items):
                if len(challenge_items) >= top_k:
                    break
                if item['rank'] > user_rank:  # 原本不符合条件的现在也加入
                    item_copy = item.copy()
                    item_copy['category'] = '冲刺'
                    item_copy['advantage'] = user_rank - item['rank']
                    challenge_items.append(item_copy)
        
        return challenge_items


class MLRecommendationEngine:
    """机器学习推荐引擎"""
    
    def __init__(self, data_service):
        """
        初始化机器学习推荐引擎
        
        Args:
            data_service: 数据服务
        """
        self.data_service = data_service
        self.logger = get_logger("MLRecommendationEngine")
        self.school_tags_cache = {}
        
        # 模拟训练好的模型（实际应该加载真实模型）
        # 这里使用简化规则模拟机器学习效果
        self.model_features = [
            'rank_gap',           # 位次差距
            'score_gap',          # 分数差距  
            'rank_ratio',         # 位次比率
            'school_level_score', # 学校层次
            'major_match_score',  # 专业匹配
            'year_trend'          # 年份趋势
        ]
        
        # 模拟特征权重（实际应由模型训练得出）
        self.feature_weights = {
            'rank_gap': 0.35,
            'score_gap': 0.20,
            'rank_ratio': 0.15,
            'school_level_score': 0.15,
            'major_match_score': 0.10,
            'year_trend': 0.05
        }
    
    def calculate_ml_features(self, student_info: Dict[str, Any], school_info: Dict[str, Any], 
                             preferences: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        计算机器学习特征
        
        Args:
            student_info: 学生信息
            school_info: 学校信息
            preferences: 用户偏好
            
        Returns:
            特征向量
        """
        try:
            # 1. 位次差距特征
            rank_gap = school_info['rank'] - student_info['rank']
            normalized_rank_gap = rank_gap / max(student_info['rank'], 1)
            
            # 2. 分数差距特征
            score_gap = school_info['score'] - student_info.get('score', 500)
            normalized_score_gap = score_gap / max(student_info.get('score', 500), 1)
            
            # 3. 位次比率特征
            rank_ratio = school_info['rank'] / max(student_info['rank'], 1)
            
            # 4. 学校层次特征
            level_score = 0
            if school_info['tags'].get('is_985'):
                level_score = 100
            elif school_info['tags'].get('is_211'):
                level_score = 80
            elif school_info['tags'].get('is_double_first_class'):
                level_score = 60
            else:
                level_score = 30
            
            # 5. 专业匹配特征
            major_match = 0
            if preferences and preferences.get('majors'):
                major_name = school_info['major_name'].lower()
                for pref_major in preferences['majors']:
                    if pref_major.lower() in major_name:
                        major_match = 100
                        break
            
            # 6. 年份趋势特征（模拟）
            # 实际应该分析多年数据得出趋势
            year_trend = 0  # 假设持平
            
            return {
                'rank_gap': normalized_rank_gap,
                'score_gap': normalized_score_gap,
                'rank_ratio': rank_ratio,
                'school_level_score': level_score / 100.0,  # 归一化
                'major_match_score': major_match / 100.0,  # 归一化
                'year_trend': year_trend
            }
            
        except Exception as e:
            self.logger.warning(f"计算特征失败: {str(e)}")
            return {feature: 0.0 for feature in self.model_features}
    
    def predict_admission_probability(self, features: Dict[str, float]) -> float:
        """
        预测录取概率（模拟模型预测）
        
        Args:
            features: 特征向量
            
        Returns:
            录取概率 (0-100)
        """
        try:
            # 模拟模型预测：加权线性组合
            # 实际应该调用真实模型：model.predict_proba(features)
            
            probability = (
                features['rank_gap'] * self.feature_weights['rank_gap'] +
                features['score_gap'] * self.feature_weights['score_gap'] +
                features['rank_ratio'] * self.feature_weights['rank_ratio'] +
                features['school_level_score'] * self.feature_weights['school_level_score'] +
                features['major_match_score'] * self.feature_weights['major_match_score'] +
                features['year_trend'] * self.feature_weights['year_trend']
            )
            
            # 转换为录取概率（调整范围到0-100）
            # rank_gap为正表示学校位次高于学生位次（容易录取）
            base_prob = 50 + probability * 50
            
            # 边界限制
            return max(1.0, min(99.0, base_prob))
            
        except Exception as e:
            self.logger.warning(f"预测概率失败: {str(e)}")
            return 50.0  # 默认概率
    
    def recommend_by_ml(self, student_info: Dict[str, Any], 
                       preferences: Optional[Dict[str, Any]] = None,
                       limit: int = 120) -> List[Dict[str, Any]]:
        """
        基于机器学习的推荐
        
        Args:
            student_info: 学生信息
            preferences: 用户偏好
            limit: 返回数量
            
        Returns:
            推荐列表
        """
        try:
            student_rank = student_info.get('rank', 0)
            self.logger.info(f"使用机器学习算法为学生位次{student_rank}生成推荐")
            
            # 获取数据
            df = self.data_service.get_data(2025)
            if df is None or df.empty:
                self.logger.error("无法获取投档数据")
                return []
            
            # 确定列名
            school_col = '招生院校' if '招生院校' in df.columns else '院校名称' if '院校名称' in df.columns else '学校名称'
            major_col = '招生专业' if '招生专业' in df.columns else '专业名称'
            rank_col = '位次' if '位次' in df.columns else '投档位次'
            score_col = '投档最低分'
            
            # 设置位次范围限制（主要推荐在学生位次上下200位范围内的学校）
            # 这样可以确保推荐结果具有实际可行性
            min_rank = student_rank - 200  # 下限：学生位次减200
            max_rank = student_rank + 100  # 上限：学生位次加100（保底范围稍宽）
            self.logger.info(f"位次范围限制: {min_rank} - {max_rank}")
            
            # 构建候选列表并预测
            candidates = []
            for _, row in df.iterrows():
                try:
                    if pd.notna(row.get(rank_col)):
                        rank_value = int(row.get(rank_col))
                        
                        # 位次范围筛选：主要推荐在合理范围内的学校
                        if rank_value < min_rank or rank_value > max_rank:
                            continue  # 跳过超出位次范围的学校
                        
                        school_name = str(row.get(school_col, '')).strip() if school_col else '未知院校'
                        major_name = str(row.get(major_col, '')).strip() if major_col else '未知专业'
                        
                        # 应用筛选条件
                        if preferences:
                            # 1. 地区筛选（只有在用户设置了偏好时才筛选）
                            if preferences.get('locations'):
                                location_score = self.calculate_location_match_score(school_name, preferences)
                                if location_score < 100:  # 100表示完全匹配，小于100表示不匹配或不确定
                                    continue  # 跳过不符合地区偏好的院校
                            
                            # 2. 专业筛选（只有在用户设置了偏好时才筛选）
                            if preferences.get('majors'):
                                major_score = self.calculate_major_match_score(major_name, preferences)
                                if major_score < 100:  # 100表示完全匹配，小于100表示不匹配
                                    continue  # 跳过不符合专业偏好的院校
                        
                        # 构建学校信息
                        school_info = {
                            'rank': rank_value,
                            'score': int(row.get(score_col, 0)) if pd.notna(row.get(score_col)) else 0,
                            'school_name': school_name,
                            'major_name': major_name,
                            'school_code': '',
                            'major_code': '',
                            'batch': '',
                            'tags': self._get_school_tags(school_name)
                        }
                        
                        # 如果有学校类型偏好，额外筛选
                        if preferences and preferences.get('school_types'):
                            tags = school_info['tags']
                            level_score = 0
                            if tags.get('is_985'):
                                level_score = 20
                            elif tags.get('is_211'):
                                level_score = 15
                            elif tags.get('is_double_first_class'):
                                level_score = 10
                            else:
                                level_score = 0
                            
                            min_level_score = 0
                            if '985' in preferences['school_types']:
                                min_level_score = max(min_level_score, 20)
                            if '211' in preferences['school_types']:
                                min_level_score = max(min_level_score, 15)
                            if '双一流' in preferences['school_types']:
                                min_level_score = max(min_level_score, 10)
                            
                            if level_score < min_level_score:
                                continue  # 跳过不符合院校层次要求的
                        
                        # 计算特征
                        features = self.calculate_ml_features(student_info, school_info, preferences)
                        
                        # 预测录取概率
                        probability = self.predict_admission_probability(features)
                        
                        # 计算排名优势
                        advantage = student_info['rank'] - rank_value
                        
                        # 确定类别和风险
                        if probability >= 80:
                            category = "保底"
                            risk_level = "低"
                        elif probability >= 60:
                            category = "稳妥"
                            risk_level = "中"
                        elif probability >= 30:
                            category = "冲刺"
                            risk_level = "高"
                        else:
                            category = "冲刺+"
                            risk_level = "极高"
                        
                        # 计算ML置信度（模拟）
                        confidence = min(95, max(60, 80 + abs(probability - 50) * 0.5))
                        
                        # 构建推荐项
                        candidate = {
                            'school_code': school_info['school_code'],
                            'school_name': school_info['school_name'],
                            'major_code': school_info['major_code'],
                            'major_name': school_info['major_name'],
                            'min_score': school_info['score'],
                            'rank': rank_value,
                            'batch': '',
                            'year': 2025,
                            'advantage': advantage,
                            'admission_probability': round(probability, 1),
                            'confidence': round(confidence, 1),  # ML置信度
                            'category': category,
                            'risk_level': risk_level,
                            'category_basis': f"ML预测:概率={probability:.1f}%,置信度={confidence:.1f}%",
                            'ml_features': features,  # 保存特征用于分析
                            'tags': school_info['tags']
                        }
                        
                        candidates.append(candidate)
                        
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"数据处理错误，跳过该行: {e}")
                    continue
            
            if not candidates:
                self.logger.error("没有符合条件的候选数据（可能筛选条件过于严格）")
                return []
            
            # 按录取概率排序
            candidates.sort(key=lambda x: x['admission_probability'], reverse=True)
            
            # 返回前N个（如果不足N个，返回实际数量）
            recommendations = candidates[:limit]
            
            self.logger.info(f"机器学习算法生成{len(recommendations)}个推荐（筛选后总计{len(candidates)}个候选）")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"机器学习推荐过程发生错误: {str(e)}")
            return []
    
    def generate_ml_volunteers(self, student_info: Dict[str, Any], 
                              preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        生成机器学习的志愿列表
        
        Args:
            student_info: 学生信息
            preferences: 用户偏好
            
        Returns:
            志愿列表
        """
        recommendations = self.recommend_by_ml(
            student_info, 
            preferences, 
            limit=120
        )
        
        # 转换为标准志愿格式
        volunteers = []
        for i, rec in enumerate(recommendations, 1):
            volunteers.append({
                'id': i,
                'school_code': rec['school_code'],
                'school_name': rec['school_name'],
                'major_code': rec['major_code'],
                'major_name': rec['major_name'],
                'min_score': rec['min_score'],
                'avg_rank_2025': rec['rank'],
                'admission_probability': rec['admission_probability'],
                'confidence': rec['confidence'],  # ML置信度
                'risk_level': rec['risk_level'],
                'category': rec['category'],
                'category_basis': rec['category_basis'],
                'notes': '',
                'tags': rec['tags'],
                'ml_features': rec['ml_features']  # 保留特征数据
            })
        
        return volunteers


class WeightedRecommendationEngine:
    """多因素加权推荐引擎"""
    
    def __init__(self, data_service):
        """
        初始化加权推荐引擎
        
        Args:
            data_service: 数据服务
        """
        self.data_service = data_service
        self.logger = get_logger("WeightedRecommendationEngine")
        self.school_tags_cache = {}  # 学校标签缓存
        
        # 权重配置
        self.weights = {
            'rank_match': 0.40,      # 位次匹配度权重
            'score_match': 0.25,     # 分数匹配度权重
            'school_level': 0.20,    # 学校层次权重
            'major_match': 0.10,     # 专业匹配权重
            'location_match': 0.05   # 地域匹配权重
        }
        
        # 学校层次评分
        self.school_level_scores = {
            'is_985': 20,
            'is_211': 15,
            'is_double_first_class': 10,
            'normal': 0
        }
    
    def calculate_rank_match_score(self, student_rank: int, school_rank: int) -> float:
        """
        计算位次匹配度分数
        
        Args:
            student_rank: 学生位次
            school_rank: 学校录取位次
            
        Returns:
            匹配度分数 (0-100)
        """
        if student_rank <= 0:
            return 0
        
        # 位次差距越小越好
        rank_gap = abs(student_rank - school_rank)
        relative_gap = rank_gap / student_rank * 100
        
        # 最大100分，差距越大分数越低
        score = max(0, 100 - relative_gap)
        return score
    
    def calculate_score_match_score(self, student_score: int, school_score: int) -> float:
        """
        计算分数匹配度分数
        
        Args:
            student_score: 学生分数
            school_score: 学校录取分数
            
        Returns:
            匹配度分数 (0-100)
        """
        if student_score <= 0:
            return 0
        
        # 分数差距越小越好（每差1分扣2分，最多扣100分）
        score_gap = abs(student_score - school_score)
        score = max(0, 100 - score_gap * 2)
        return score
    
    def calculate_school_level_score(self, tags: Dict[str, bool]) -> float:
        """
        计算学校层次分数
        
        Args:
            tags: 学校标签字典
            
        Returns:
            层次分数
        """
        if tags.get('is_985'):
            return self.school_level_scores['is_985']
        elif tags.get('is_211'):
            return self.school_level_scores['is_211']
        elif tags.get('is_double_first_class'):
            return self.school_level_scores['is_double_first_class']
        else:
            return self.school_level_scores['normal']
    
    def calculate_major_match_score(self, major_name: str, preferences: Optional[Dict[str, Any]]) -> float:
        """
        计算专业匹配度分数
        
        Args:
            major_name: 专业名称
            preferences: 用户偏好
            
        Returns:
            匹配度分数
        """
        if not preferences:
            return 30  # 默认基础分
        
        preferred_majors = preferences.get('majors', [])
        if not preferred_majors:
            return 30
        
        # 检查是否包含偏好专业
        for major in preferred_majors:
            if major in major_name:
                return 100
        
        return 30
    
    def calculate_location_match_score(self, school_name: str, preferences: Optional[Dict[str, Any]]) -> float:
        """
        计算地域匹配度分数
        
        Args:
            school_name: 学校名称
            preferences: 用户偏好
            
        Returns:
            匹配度分数
        """
        if not preferences:
            return 50  # 默认基础分
        
        preferred_locations = preferences.get('locations', [])
        if not preferred_locations:
            return 50
        
        try:
            # 获取学校信息以判断所在地
            school_info_df = self.data_service.load_school_info()
            if school_info_df is None or school_info_df.empty:
                return 50
            
            # 确定列名
            school_col = '学校名称' if '学校名称' in school_info_df.columns else '院校名称'
            
            # 查找学校
            school_row = school_info_df[school_info_df[school_col] == school_name]
            if school_row.empty:
                return 50
            
            # 获取学校所在城市/区域
            city = school_row.iloc[0].get('所在城市', '')
            region = school_row.iloc[0].get('所在区域', '')
            
            # 检查是否匹配偏好地区
            location_str = f"{city}{region}"
            for pref_location in preferred_locations:
                if pref_location in location_str:
                    return 100  # 完全匹配
            
            # 如果没有匹配，给较低分数
            return 20
            
        except Exception as e:
            self.logger.warning(f"地域匹配计算失败 {school_name}: {str(e)}")
            return 50
    
    def calculate_weighted_score(self, student_info: Dict[str, Any], 
                                school_info: Dict[str, Any],
                                preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        计算综合加权得分
        
        Args:
            student_info: 学生信息 {rank, score}
            school_info: 学校信息 {rank, score, school_name, major_name, tags}
            preferences: 用户偏好
            
        Returns:
            综合评分结果
        """
        try:
            # 计算各项得分
            rank_score = self.calculate_rank_match_score(
                student_info['rank'], 
                school_info['rank']
            )
            
            score_score = self.calculate_score_match_score(
                student_info.get('score', 0),
                school_info['score']
            )
            
            level_score = self.calculate_school_level_score(school_info['tags'])
            
            major_score = self.calculate_major_match_score(
                school_info['major_name'],
                preferences
            )
            
            location_score = self.calculate_location_match_score(
                school_info['school_name'],
                preferences
            )
            
            # 计算加权总分
            total_score = (
                rank_score * self.weights['rank_match'] +
                score_score * self.weights['score_match'] +
                level_score * self.weights['school_level'] +
                major_score * self.weights['major_match'] +
                location_score * self.weights['location_match']
            )
            
            return {
                'total_score': round(total_score, 2),
                'rank_score': round(rank_score, 2),
                'score_score': round(score_score, 2),
                'level_score': level_score,
                'major_score': major_score,
                'location_score': location_score
            }
            
        except Exception as e:
            self.logger.warning(f"计算加权分数失败: {str(e)}")
            return {
                'total_score': 0,
                'rank_score': 0,
                'score_score': 0,
                'level_score': 0,
                'major_score': 0,
                'location_score': 0
            }
    
    def determine_category_enhanced(self, advantage: int, score: float) -> tuple:
        """
        改进的志愿类别判断（基于排名优势和综合得分）
        
        位次规则说明：
        - 保底：录取位次 > 学生位次 且 ≤ (学生位次+100)，即 0 < advantage ≤ 100
        - 稳健：录取位次在 (学生位次-100) 至 (学生位次+100) 之间，即 -100 ≤ advantage ≤ 100
        - 冲刺：录取位次在 (学生位次-200) 至 学生位次 之间，即 -200 ≤ advantage ≤ 0
        
        Args:
            advantage: 排名优势 = 学生位次 - 录取位次
            score: 综合得分
            
        Returns:
            (类别, 风险等级, 录取概率)
        """
        # 基于排名优势的类别判断（根据新的位次规则）
        if advantage > 100:
            category = "保底"
            risk_level = "极低"
            probability = min(95, 70 + (advantage - 100) * 0.05)
        elif advantage > 0:
            category = "保底"
            risk_level = "低"
            probability = min(90, 50 + advantage * 0.4)
        elif advantage >= -100:
            category = "稳健"
            risk_level = "中"
            probability = max(30, min(70, 50 + advantage * 0.2))
        elif advantage >= -200:
            category = "冲刺"
            risk_level = "高"
            probability = max(10, min(50, 30 + (advantage + 100) * 0.2))
        else:
            category = "冲刺+"
            risk_level = "极高"
            probability = max(1, min(30, 10 + (advantage + 200) * 0.1))
        
        # 综合得分调整（得分越高，概率适当提高）
        if score >= 70:
            probability = min(99, probability * 1.1)
        elif score >= 50:
            probability = min(99, probability * 1.05)
        
        return category, risk_level, round(probability, 1)
    
    def recommend_by_weighted_score(self, student_info: Dict[str, Any], 
                                   preferences: Optional[Dict[str, Any]] = None,
                                   limit: int = 120) -> List[Dict[str, Any]]:
        """
        基于多因素加权评分的推荐
        
        Args:
            student_info: 学生信息 {rank, score, ...}
            preferences: 用户偏好 {majors, locations, school_types, ...}
            limit: 返回数量
            
        Returns:
            推荐列表
        """
        try:
            student_rank = student_info.get('rank', 0)
            
            # 获取基础数据
            df = self.data_service.get_data(2025)
            if df is None or df.empty:
                self.logger.error("无法获取投档数据")
                return []
            
            # 确定列名
            school_col = '招生院校' if '招生院校' in df.columns else '院校名称' if '院校名称' in df.columns else '学校名称'
            major_col = '招生专业' if '招生专业' in df.columns else '专业名称'
            rank_col = '位次' if '位次' in df.columns else '投档位次'
            score_col = '投档最低分'
            
            # 设置位次范围限制（主要推荐在学生位次上下200位范围内的学校）
            min_rank = student_rank - 200  # 下限：学生位次减200
            max_rank = student_rank + 100  # 上限：学生位次加100（保底范围稍宽）
            self.logger.info(f"位次范围限制: {min_rank} - {max_rank}")
            
            # 构建候选列表并计算加权分数
            candidates = []
            for _, row in df.iterrows():
                try:
                    if pd.notna(row.get(rank_col)):
                        rank_value = int(row.get(rank_col))
                        
                        # 位次范围筛选：主要推荐在合理范围内的学校
                        if rank_value < min_rank or rank_value > max_rank:
                            continue  # 跳过超出位次范围的学校
                        
                        school_name = str(row.get(school_col, '')).strip() if school_col else '未知院校'
                        major_name = str(row.get(major_col, '')).strip() if major_col else '未知专业'
                        
                        # 计算各项信息
                        school_info = {
                            'rank': rank_value,
                            'score': int(row.get(score_col, 0)) if pd.notna(row.get(score_col)) else 0,
                            'school_name': school_name,
                            'major_name': major_name,
                            'school_code': '',
                            'major_code': '',
                            'batch': '',
                            'tags': self._get_school_tags(school_name)
                        }
                        
                        # 应用筛选条件
                        if preferences:
                            # 1. 地区筛选（只有在用户设置了偏好时才筛选）
                            if preferences.get('locations'):
                                location_score = self.calculate_location_match_score(school_name, preferences)
                                if location_score < 100:  # 100表示完全匹配，小于100表示不匹配或不确定
                                    continue  # 跳过不符合地区偏好的院校
                            
                            # 2. 专业筛选（只有在用户设置了偏好时才筛选）
                            if preferences.get('majors'):
                                major_score = self.calculate_major_match_score(major_name, preferences)
                                if major_score < 100:  # 100表示完全匹配，小于100表示不匹配
                                    continue  # 跳过不符合专业偏好的院校
                        
                        # 计算加权总分
                        scores = self.calculate_weighted_score(student_info, school_info, preferences)
                        
                        # 如果有学校类型偏好，额外筛选
                        if preferences and preferences.get('school_types'):
                            school_type_score = scores['level_score']
                            min_level_score = 0
                            if '985' in preferences['school_types']:
                                min_level_score = max(min_level_score, 20)
                            if '211' in preferences['school_types']:
                                min_level_score = max(min_level_score, 15)
                            if '双一流' in preferences['school_types']:
                                min_level_score = max(min_level_score, 10)
                            
                            if school_type_score < min_level_score:
                                continue  # 跳过不符合院校层次要求的
                        
                        # 计算排名优势
                        advantage = student_info['rank'] - rank_value
                        
                        # 确定类别、风险、概率
                        category, risk_level, probability = self.determine_category_enhanced(advantage, scores['total_score'])
                        
                        # 构建推荐项
                        candidate = {
                            'school_code': school_info['school_code'],
                            'school_name': school_info['school_name'],
                            'major_code': school_info['major_code'],
                            'major_name': school_info['major_name'],
                            'min_score': school_info['score'],
                            'rank': rank_value,
                            'batch': '',
                            'year': 2025,
                            'advantage': advantage,
                            'total_score': scores['total_score'],
                            'category': category,
                            'risk_level': risk_level,
                            'admission_probability': probability,
                            'score_details': scores,  # 详细分数
                            'tags': school_info['tags']
                        }
                        
                        candidates.append(candidate)
                        
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"数据处理错误，跳过该行: {e}")
                    continue
            
            if not candidates:
                self.logger.error("没有符合条件的候选数据（可能筛选条件过于严格）")
                return []
            
            # 按综合得分排序
            candidates.sort(key=lambda x: x['total_score'], reverse=True)
            
            # 返回前N个（如果不足N个，返回实际数量）
            recommendations = candidates[:limit]
            
            self.logger.info(f"为学生生成{len(recommendations)}个加权推荐（筛选后总计{len(candidates)}个候选）")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"加权推荐过程发生错误: {str(e)}")
            return []
    
    def generate_weighted_volunteers(self, student_info: Dict[str, Any], 
                                   preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        生成多因素加权的志愿列表
        
        Args:
            student_info: 学生信息 {rank, score, ...}
            preferences: 用户偏好
            
        Returns:
            志愿列表
        """
        recommendations = self.recommend_by_weighted_score(
            student_info, 
            preferences, 
            limit=120
        )
        
        # 转换为标准志愿格式
        volunteers = []
        for i, rec in enumerate(recommendations, 1):
            volunteers.append({
                'id': i,
                'school_code': rec['school_code'],
                'school_name': rec['school_name'],
                'major_code': rec['major_code'],
                'major_name': rec['major_name'],
                'min_score': rec['min_score'],
                'avg_rank_2025': rec['rank'],
                'admission_probability': rec['admission_probability'],
                'risk_level': rec['risk_level'],
                'category': rec['category'],
                'category_basis': f"综合得分:{rec['total_score']} | 排名优势:{rec['advantage']}",
                'notes': '',
                'tags': rec['tags']
            })
        
        return volunteers
    
    def _get_school_tags(self, school_name: str) -> Dict[str, bool]:
        """
        获取学校标签（复用原有逻辑）
        """
        if not school_name:
            return {
                'is_985': False, 'is_211': False, 'is_double_first_class': False,
                'is_private': False, 'is_independent': False,
                'is_chinese_foreign': False, 'is_hk_macao_taiwan': False
            }
        
        if school_name in self.school_tags_cache:
            return self.school_tags_cache[school_name]
        
        try:
            school_df = self.data_service.load_school_info()
            if school_df is None or school_df.empty:
                tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False,
                       'is_private': False, 'is_independent': False,
                       'is_chinese_foreign': False, 'is_hk_macao_taiwan': False}
                self.school_tags_cache[school_name] = tags
                return tags
            
            school_col = '学校名称' if '学校名称' in school_df.columns else '院校名称'
            school_row = school_df[school_df[school_col] == school_name]
            
            if school_row.empty:
                tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False,
                       'is_private': False, 'is_independent': False,
                       'is_chinese_foreign': False, 'is_hk_macao_taiwan': False}
                self.school_tags_cache[school_name] = tags
                return tags
            
            row = school_row.iloc[0]
            
            def to_bool(value):
                if pd.isna(value):
                    return False
                return str(value).strip().upper() == 'Y'
            
            tags = {
                'is_985': to_bool(row.get('985', '')),
                'is_211': False,
                'is_double_first_class': to_bool(row.get('双一流', '')),
                'is_private': to_bool(row.get('民办高校', '')),
                'is_independent': to_bool(row.get('独立学院', '')),
                'is_chinese_foreign': to_bool(row.get('中外合作办学', '')),
                'is_hk_macao_taiwan': to_bool(row.get('内地与港澳台合作办学', ''))
            }
            
            if tags['is_985']:
                tags['is_211'] = True
            
            self.school_tags_cache[school_name] = tags
            return tags
            
        except Exception as e:
            self.logger.warning(f"获取学校标签失败 {school_name}: {str(e)}")
            tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False,
                   'is_private': False, 'is_independent': False,
                   'is_chinese_foreign': False, 'is_hk_macao_taiwan': False}
            self.school_tags_cache[school_name] = tags
            return tags


# 保持原有的纯排名推荐引擎作为备选
class RecommendationEngine(WeightedRecommendationEngine):
    """兼容原有接口的推荐引擎"""
    
    def __init__(self, data_service):
        """初始化"""
        super().__init__(data_service)
        self.logger = get_logger("RecommendationEngine")
    
    def recommend_by_rank(self, student_rank: int, limit: int = 120) -> List[Dict[str, Any]]:
        """
        兼容原有接口：基于排名的推荐
        """
        student_info = {'rank': student_rank, 'score': 500}  # 默认分数
        recommendations = self.recommend_by_weighted_score(student_info, limit=limit)
        
        # 转换为原有格式
        result = []
        for rec in recommendations:
            result.append({
                'school_code': rec['school_code'],
                'school_name': rec['school_name'],
                'major_code': rec['major_code'],
                'major_name': rec['major_name'],
                'min_score': rec['min_score'],
                'rank': rec['rank'],
                'batch': rec['batch'],
                'year': rec['year'],
                'category': rec['category'],
                'advantage': rec['advantage']
            })
        
        return result
    
    def generate_recommendation(self, student_data: Dict[str, Any], 
                               num_recommendations: int = 120) -> List[Dict[str, Any]]:
        """
        兼容原有接口：生成志愿推荐
        """
        return self.generate_weighted_volunteers(student_data)
    
    def recommend_by_rank(self, student_rank: int, limit: int = 120) -> List[Dict[str, Any]]:
        """
        基于排名推荐院校专业（主要推荐方法）
        完全忽略分数差异，仅基于学生位次与专业录取位次的比较
        
        Args:
            student_rank: 学生位次（数值越小竞争力越强）
            limit: 返回数量
        
        Returns:
            推荐列表
        """
        try:
            # 获取数据
            df = self.data_service.get_data(2025)
            if df is None or df.empty:
                self.logger.error("无法获取投档数据")
                return []
            
            # 确定列名
            school_col = '招生院校' if '招生院校' in df.columns else '院校名称' if '院校名称' in df.columns else '学校名称'
            major_col = '招生专业' if '招生专业' in df.columns else '专业名称'
            rank_col = '位次' if '位次' in df.columns else '投档位次'
            score_col = '投档最低分'
            batch_col = '批次' if '批次' in df.columns else ''
            
            # 转换为字典列表，准备排名推荐
            items = []
            for _, row in df.iterrows():
                try:
                    # 检查必要的排名数据是否存在
                    if pd.notna(row.get(rank_col)):
                        rank_value = int(row.get(rank_col))
                        # 学生位次越小越好，录取位次越大对学生越有利
                        items.append({
                            'school_code': '',  # 院校编号可能不存在，用空字符串
                            'school_name': str(row.get(school_col, '')).strip() if school_col else '未知院校',
                            'major_code': '',  # 专业编号可能不存在，用空字符串
                            'major_name': str(row.get(major_col, '')).strip() if major_col else '未知专业',
                            'min_score': int(row.get(score_col, 0)) if pd.notna(row.get(score_col)) else 0,
                            'rank': rank_value,  # 录取位次（数值越大表示越容易录取）
                            'batch': str(row.get(batch_col, '')).strip() if batch_col else '',
                            'year': 2025
                        })
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"数据转换错误，跳过该行: {e}")
                    continue
            
            if not items:
                self.logger.error("没有有效的录取数据可用于推荐")
                return []
            
            # 使用纯排名推荐器
            recommender = PureRankRecommender(items)
            recommendations = recommender.recommend(student_rank, strategy="balanced", top_k=limit)
            
            self.logger.info(f"为学生位次{student_rank}生成{len(recommendations)}个排名推荐")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"推荐过程发生错误: {str(e)}")
            return []
    
    def recommend_by_score(self, score: int, rank: Optional[int] = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """
        兼容性别名方法，实际调用基于排名的推荐
        
        Args:
            score: 考生分数（忽略）
            rank: 考生位次（实际使用此参数）
            limit: 返回数量
        
        Returns:
            推荐列表
        """
        if rank is None:
            self.logger.warning("recommend_by_score被调用但未提供rank参数，无法基于排名推荐")
            return []
        
        # 直接调用基于排名的推荐方法
        return self.recommend_by_rank(rank, limit)
        
    def generate_recommendation(self, student_data: Dict[str, Any], 
                               num_recommendations: int = 120) -> List[Dict[str, Any]]:
        """
        生成志愿推荐（主要对外接口）
        完全基于排名比较，忽略分数差异
        
        Args:
            student_data: 学生信息 {rank: 位次, ...}
            num_recommendations: 推荐数量
        
        Returns:
            志愿推荐列表
        """
        student_rank = student_data.get('rank')
        if not student_rank:
            self.logger.error("学生位次信息缺失")
            return []
        
        # 使用基于排名的推荐方法
        raw_recommendations = self.recommend_by_rank(student_rank, limit=num_recommendations)
        
        # 转换为标准志愿格式
        volunteers = []
        for i, rec in enumerate(raw_recommendations, 1):
            advantage = rec.get('advantage', 0)
            school_name = rec.get('school_name', '')
            
            # 计算录取概率和风险等级
            admission_probability = self._calculate_admission_probability(advantage)
            risk_level = self._calculate_risk_level(advantage)
            category = rec.get('category', '匹配')
            category_basis = f"排名优势:{advantage}"
            
            # 获取学校标签
            tags = self._get_school_tags(school_name)
            
            volunteers.append({
                'id': i,
                'school_code': rec.get('school_code', ''),
                'school_name': school_name,
                'major_code': rec.get('major_code', ''),
                'major_name': rec.get('major_name', ''),
                'min_score': rec.get('min_score', 0),
                'avg_rank_2025': rec.get('rank', 0),
                'admission_probability': round(admission_probability, 1),
                'risk_level': risk_level,
                'category': category,
                'category_basis': category_basis,
                'notes': '',
                'tags': tags  # 添加学校标签
            })
        
        self.logger.info(f"为学生位次{student_rank}生成{len(volunteers)}个纯排名推荐志愿")
        return volunteers
    
    def _calculate_risk_level(self, advantage: int) -> str:
        """
        根据排名优势计算风险等级
        
        基于新的位次范围规则：
        - 保底（advantage > 0）：极低或低风险
        - 稳健（-100 ≤ advantage ≤ 100）：中等风险
        - 冲刺（-200 ≤ advantage < 0）：高或极高风险
        
        Args:
            advantage: 排名优势
        
        Returns:
            风险等级：极低、低、中、高、极高
        """
        if advantage > 100:
            return "极低"
        elif advantage > 0:
            return "低"
        elif advantage >= -100:
            return "中"
        elif advantage >= -200:
            return "高"
        else:
            return "极高"
    
    def _get_school_tags(self, school_name: str) -> Dict[str, bool]:
        """
        获取学校标签（985、211、双一流等）
        
        Args:
            school_name: 学校名称
            
        Returns:
            标签字典
        """
        if not school_name:
            return {
                'is_985': False,
                'is_211': False,
                'is_double_first_class': False,
                'is_private': False,
                'is_independent': False,
                'is_chinese_foreign': False,
                'is_hk_macao_taiwan': False
            }
        
        # 检查缓存
        if school_name in self.school_tags_cache:
            return self.school_tags_cache[school_name]
        
        try:
            # 加载学校信息
            school_df = self.data_service.load_school_info()
            if school_df is None or school_df.empty:
                self.logger.warning("无法加载学校信息数据")
                # 返回默认值
                tags = {
                    'is_985': False,
                    'is_211': False,
                    'is_double_first_class': False,
                    'is_private': False,
                    'is_independent': False,
                    'is_chinese_foreign': False,
                    'is_hk_macao_taiwan': False
                }
                self.school_tags_cache[school_name] = tags
                return tags
            
            # 确定学校名称列（可能是 '学校名称' 或 '院校名称'）
            school_col = '学校名称' if '学校名称' in school_df.columns else '院校名称'
            
            # 查找学校
            school_row = school_df[school_df[school_col] == school_name]
            
            if school_row.empty:
                # 学校不存在于信息表中
                tags = {
                    'is_985': False,
                    'is_211': False,
                    'is_double_first_class': False,
                    'is_private': False,
                    'is_independent': False,
                    'is_chinese_foreign': False,
                    'is_hk_macao_taiwan': False
                }
                self.school_tags_cache[school_name] = tags
                return tags
            
            # 获取标签
            row = school_row.iloc[0]
            
            # 转换 Y/空 为 True/False
            def to_bool(value):
                if pd.isna(value):
                    return False
                return str(value).strip().upper() == 'Y'
            
            tags = {
                'is_985': to_bool(row.get('985', '')),
                'is_211': False,  # 数据中没有直接的211字段，需要从名称或其他方式判断
                'is_double_first_class': to_bool(row.get('双一流', '')),
                'is_private': to_bool(row.get('民办高校', '')),
                'is_independent': to_bool(row.get('独立学院', '')),
                'is_chinese_foreign': to_bool(row.get('中外合作办学', '')),
                'is_hk_macao_taiwan': to_bool(row.get('内地与港澳台合作办学', ''))
            }
            
            # 特殊判断：很多985学校也是211
            if tags['is_985']:
                tags['is_211'] = True
            
            # 缓存结果
            self.school_tags_cache[school_name] = tags
            return tags
            
        except Exception as e:
            self.logger.warning(f"获取学校标签失败 {school_name}: {str(e)}")
            # 返回默认值
            tags = {
                'is_985': False,
                'is_211': False,
                'is_double_first_class': False,
                'is_private': False,
                'is_independent': False,
                'is_chinese_foreign': False,
                'is_hk_macao_taiwan': False
            }
            self.school_tags_cache[school_name] = tags
            return tags
    
    def _calculate_admission_probability(self, advantage: int) -> float:
        """
        根据排名优势计算录取概率（仅基于排名比较）
        
        基于新的位次范围规则：
        - 保底（advantage > 100）：70%-95%录取概率
        - 稳健（-100 ≤ advantage ≤ 100）：30%-90%录取概率
        - 冲刺（-200 ≤ advantage < 0）：10%-50%录取概率
        
        Args:
            advantage: 排名优势 = 学生位次 - 录取位次
                     正数：学生排名更靠前（优势），负数：学生排名更靠后（劣势）
        
        Returns:
            录取概率 (0-100)
        """
        if advantage > 100:
            # 强保底：学生排名明显靠前
            return min(95.0, 70.0 + (advantage - 100) * 0.05)
        elif advantage > 0:
            # 保底：学生排名稍靠前
            return min(90.0, 50.0 + advantage * 0.4)
        elif advantage >= -100:
            # 稳健/匹配：学生排名相当
            return max(30.0, min(70.0, 50.0 + advantage * 0.2))
        elif advantage >= -200:
            # 冲刺：学生排名稍靠后，但差距不大
            return max(10.0, min(50.0, 30.0 + (advantage + 100) * 0.2))
        else:
            # 超出冲刺范围，概率很低
            return max(1.0, min(30.0, 10.0 + (advantage + 200) * 0.1))
    
    def _determine_category_by_advantage(self, advantage: int) -> str:
        """
        根据排名优势确定志愿类别
        
        基于新的位次范围规则：
        - 保底：录取位次 > 学生位次（advantage > 0）
        - 稳健：录取位次在(学生位次-100)至(学生位次+100)之间（-100 ≤ advantage ≤ 100）
        - 冲刺：录取位次在(学生位次-200)至学生位次之间（-200 ≤ advantage < 0）
        
        Args:
            advantage: 排名优势
        
        Returns:
            类别：保底、稳健、冲刺
        """
        if advantage > 100:
            return "保底"      # 学生排名明显靠前，强保底
        elif advantage > 0:
            return "保底"      # 学生排名稍靠前，保底
        elif advantage >= -100:
            return "稳健"      # 学生排名接近，稳健匹配
        elif advantage >= -200:
            return "冲刺"      # 学生排名稍靠后，合理冲刺
        else:
            return "冲刺"      # 超出范围，但仍尝试冲刺
    
    def smart_recommend(self, student_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能推荐（多策略组合）
        
        Args:
            student_info: 学生信息 {score, rank, province, subjects, is_arts, ...}
        
        Returns:
            推荐结果字典
        """
        rank = student_info.get('rank')
        if not rank:
            return {'success': False, 'error': '缺少位次信息'}
        
        # 使用纯排名推荐器生成不同策略的推荐
        df = self.data_service.get_data(2025)
        if df is None or df.empty:
            return {'success': False, 'error': '无法获取投档数据'}
        
        # 准备数据
        school_col = '招生院校' if '招生院校' in df.columns else '院校名称' if '院校名称' in df.columns else '学校名称'
        major_col = '招生专业' if '招生专业' in df.columns else '专业名称'
        rank_col = '位次' if '位次' in df.columns else '投档位次'
        score_col = '投档最低分'
        
        items = []
        for _, row in df.iterrows():
            try:
                if pd.notna(row.get(rank_col)):
                    rank_value = int(row.get(rank_col))
                    items.append({
                        'school_code': '',
                        'school_name': str(row.get(school_col, '')).strip() if school_col else '未知院校',
                        'major_code': '',
                        'major_name': str(row.get(major_col, '')).strip() if major_col else '未知专业',
                        'min_score': int(row.get(score_col, 0)) if pd.notna(row.get(score_col)) else 0,
                        'rank': rank_value,
                        'batch': '',
                        'year': 2025
                    })
            except (ValueError, TypeError):
                continue
        
        if not items:
            return {'success': False, 'error': '没有有效的录取数据'}
        
        # 生成不同策略的推荐
        recommender = PureRankRecommender(items)
        conservative_rec = recommender.recommend(rank, strategy="conservative", top_k=40)
        balanced_rec = recommender.recommend(rank, strategy="balanced", top_k=120)
        aggressive_rec = recommender.recommend(rank, strategy="aggressive", top_k=40)
        
        return {
            'success': True,
            'data': {
                'conservative': conservative_rec,
                'balanced': balanced_rec, 
                'aggressive': aggressive_rec,
                'student_rank': rank
            }
        }
    
    
    def generate_volunteers(self, student_info: Dict[str, Any], 
                           preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        为学生生成志愿推荐列表
        
        Args:
            student_info: 学生信息，包含分数、排名等
            preferences: 偏好设置，如地区偏好、学校类型等
            
        Returns:
            志愿推荐列表
        """
        rank = student_info.get('rank')
        if not rank:
            self.logger.error("学生位次信息缺失")
            return []
        
        # 使用 generate_recommendation 来生成完整的志愿信息（包含序号、风险等）
        student_data = {'rank': rank}
        return self.generate_recommendation(student_data, num_recommendations=120)
    
    def _create_volunteer(self, row, index: int, type_str: str, student_score: int) -> Dict[str, Any]:
        """创建志愿字典"""
        import hashlib
        from datetime import datetime
        
        # 计算录取概率（简单估算）
        diff = student_score - row['投档最低分']
        if diff >= 20:
            probability = 85 + min(10, (diff - 20) // 2)
        elif diff >= 10:
            probability = 70 + min(15, (diff - 10))
        elif diff >= 0:
            probability = 50 + min(20, diff * 2)
        else:
            probability = 30 + min(20, (diff + 20) // 2)
        
        probability = max(10, min(99, probability))
        
        # 尝试不同的学校列名
        school_cols = ['招生院校', '院校名称', '学校名称']
        school_name = None
        for col in school_cols:
            if col in row:
                school_name = row[col]
                break
        if school_name is None:
            # 如果没有找到，使用第一个列名
            school_name = row.index[0] if len(row.index) > 0 else "未知学校"
        
        # 尝试不同的专业列名
        major_cols = ['招生专业', '专业名称']
        major = None
        for col in major_cols:
            if col in row:
                major = row[col]
                break
        if major is None:
            # 如果没有找到，使用第二个列名
            major = row.index[1] if len(row.index) > 1 else "未知专业"
        
        # 生成学校代码（使用哈希）
        school_code = str(int(hashlib.md5(str(school_name).encode('utf-8')).hexdigest(), 16) % 100000)
        
        # 计算风险等级
        if probability >= 70:
            risk_level = "低"
        elif probability >= 30:
            risk_level = "中"
        else:
            risk_level = "高"
        
        # 生成类别依据
        category_basis_map = {
            '冲': "分数略低于往年录取线",
            '稳': "分数与往年录取线相当",
            '推荐': "综合推荐",
            '保': "分数高于往年录取线"
        }
        category_basis = category_basis_map.get(type_str, "未知依据")
        
        # 获取位次信息
        rank_cols = ['投档位次', '位次']
        avg_rank_2025 = None
        for col in rank_cols:
            if col in row:
                try:
                    avg_rank_2025 = int(row[col])
                except (ValueError, TypeError):
                    avg_rank_2025 = None
                break
        
        return {
            'id': f'v_{index:03d}',
            'school_name': school_name,
            'university_code': school_code,
            'major_name': major,
            'admission_probability': probability,
            'category': type_str,
            'risk_level': risk_level,
            'category_basis': category_basis,
            'avg_rank_2025': avg_rank_2025,
            'province': '',  # 暂时留空，需要学校位置信息
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tags': {
                'is_985': False,  # 需要学校类型信息
                'is_211': False,
                'is_double_first_class': False,
                'is_private': False,
                'is_independent': False
            }
        }


# 统一推荐引擎（支持多算法切换）
class RecommendationEngine:
    """统一推荐引擎 - 支持多算法切换"""
    
    def __init__(self, data_service):
        """
        初始化统一推荐引擎
        
        Args:
            data_service: 数据服务
        """
        self.data_service = data_service
        self.logger = get_logger("RecommendationEngine")
        
        # 初始化所有算法引擎
        self.ml_engine = MLRecommendationEngine(data_service)
        self.weighted_engine = WeightedRecommendationEngine(data_service)
        
        # 默认算法
        self.default_algorithm = 'weighted'  # 默认使用加权算法
        
        self.logger.info("统一推荐引擎初始化完成，支持算法：ml, weighted")
    
    def set_default_algorithm(self, algorithm: str):
        """
        设置默认推荐算法
        
        Args:
            algorithm: 算法名称 ('ml' 或 'weighted')
        """
        if algorithm in ['ml', 'weighted']:
            self.default_algorithm = algorithm
            self.logger.info(f"默认算法设置为: {algorithm}")
        else:
            self.logger.warning(f"不支持的算法: {algorithm}")
    
    def generate_volunteers(self, student_info: Dict[str, Any], 
                           preferences: Optional[Dict[str, Any]] = None,
                           algorithm: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        生成志愿（支持算法选择）
        
        Args:
            student_info: 学生信息
            preferences: 用户偏好
            algorithm: 算法选择 ('ml', 'weighted', 或 None使用默认)
            
        Returns:
            志愿列表
        """
        # 确定使用哪种算法
        algo = algorithm or self.default_algorithm
        
        self.logger.info(f"使用算法 '{algo}' 为学生生成志愿")
        
        if algo == 'ml':
            # 机器学习算法
            return self.ml_engine.generate_ml_volunteers(student_info, preferences)
        else:
            # 加权评分算法（默认）
            return self.weighted_engine.generate_weighted_volunteers(student_info, preferences)
    
    def recommend_by_rank(self, student_rank: int, limit: int = 120) -> List[Dict[str, Any]]:
        """
        兼容原有接口：基于排名的推荐
        """
        student_info = {'rank': student_rank, 'score': 500}
        
        # 使用加权算法（与原有逻辑兼容）
        recommendations = self.weighted_engine.recommend_by_weighted_score(student_info, limit=limit)
        
        # 转换为原有格式
        result = []
        for rec in recommendations:
            result.append({
                'school_code': rec['school_code'],
                'school_name': rec['school_name'],
                'major_code': rec['major_code'],
                'major_name': rec['major_name'],
                'min_score': rec['min_score'],
                'rank': rec['rank'],
                'batch': rec['batch'],
                'year': rec['year'],
                'category': rec['category'],
                'advantage': rec['advantage']
            })
        
        return result
    
    def generate_recommendation(self, student_data: Dict[str, Any], 
                               num_recommendations: int = 120,
                               algorithm: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        兼容原有接口：生成志愿推荐（支持算法选择）
        """
        return self.generate_volunteers(student_data, None, algorithm)
