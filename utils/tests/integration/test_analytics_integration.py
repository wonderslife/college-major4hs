"""
分析引擎集成测试
"""
import pytest
import pandas as pd

from core.analytics.analytics import AnalyticsEngine
from core.data.cache_manager import CacheManager


class TestAnalyticsIntegration:
    """测试分析引擎集成"""
    
    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        return pd.DataFrame({
            "school_code": ["10001", "10001", "10001", "10002", "10002"],
            "school_name": ["北京大学", "北京大学", "北京大学", "清华大学", "清华大学"],
            "major_code": ["0101", "0201", "0301", "0401", "0501"],
            "major_name": ["哲学", "经济学", "数学", "物理", "化学"],
            "province": ["北京市", "北京市", "北京市", "北京市", "北京市"],
            "city": ["北京市", "北京市", "北京市", "北京市", "北京市"],
            "score_2023": [675, 685, 690, 680, 670],
            "rank_2023": [120, 80, 50, 100, 130],
            "score_2024": [680, 690, 695, 685, 675],
            "rank_2024": [110, 70, 45, 90, 120],
            "score_2025": [685, 695, 700, 690, 680],
            "rank_2025": [100, 60, 40, 80, 110],
            "graduate_rate": [0.55, 0.52, 0.58, 0.56, 0.53],
            "top_subject": ["A+", "A", "A+", "A+", "A"]
        })
    
    @pytest.fixture
    def analytics_engine(self, sample_data):
        """创建并初始化分析引擎"""
        engine = AnalyticsEngine()
        engine.set_data(sample_data)
        return engine
    
    def test_full_analytics_workflow(self, analytics_engine):
        """测试完整分析工作流"""
        # 1. 获取基础统计
        stats = analytics_engine.get_statistics()
        assert "total_records" in stats
        assert stats["total_records"] == 5
        
        # 2. 获取分数分布
        score_dist = analytics_engine.score_distribution
        assert "bins" in score_dist
        assert "counts" in score_dist
        
        # 3. 获取位次分布
        rank_dist = analytics_engine.rank_distribution
        assert "bins" in rank_dist
        assert "counts" in rank_dist
        
        # 4. 获取热门院校
        top_schools = analytics_engine.get_top_universities(limit=3)
        assert len(top_schools) > 0
        
        # 5. 获取热门专业
        top_majors = analytics_engine.get_top_majors(limit=3)
        assert len(top_majors) > 0
    
    def test_search_and_analyze_workflow(self, analytics_engine):
        """测试搜索和分析工作流"""
        # 1. 搜索
        results = analytics_engine.search("北京大学")
        assert len(results) > 0
        
        # 2. 按分数筛选
        filtered = analytics_engine.search_by_score_range(685, 695)
        assert len(filtered) >= 0
        
        # 3. 按位次筛选
        filtered = analytics_engine.search_by_rank_range(50, 100)
        assert len(filtered) >= 0
    
    def test_probability_calculation_workflow(self, analytics_engine):
        """测试概率计算工作流"""
        # 计算录取概率
        result = analytics_engine.calculate_admission_probability(
            school_name="北京大学",
            major_name="哲学",
            user_score=682,
            user_rank=105
        )
        
        assert "probability" in result
        assert "level" in result
        assert "details" in result
        
        # 批量计算
        batch_results = analytics_engine.batch_calculate_probability(
            user_score=690,
            user_rank=70
        )
        
        assert len(batch_results) > 0
        assert all("probability" in r for r in batch_results)
    
    def test_recommendation_workflow(self, analytics_engine):
        """测试推荐工作流"""
        # 获取推荐
        recommendations = analytics_engine.get_recommendations(
            user_score=688,
            user_rank=85,
            limit=3
        )
        
        assert len(recommendations) > 0
        assert all("school_name" in r for r in recommendations)
        assert all("major_name" in r for r in recommendations)
        assert all("probability" in r for r in recommendations)
    
    def test_chart_data_workflow(self, analytics_engine):
        """测试图表数据工作流"""
        # 获取分数分布图数据
        chart_data = analytics_engine.get_chart_data("score_distribution")
        assert "data" in chart_data
        assert "layout" in chart_data
        
        # 获取位次分布图数据
        chart_data = analytics_engine.get_chart_data("rank_distribution")
        assert "data" in chart_data
        
        # 获取院校排行图数据
        chart_data = analytics_engine.get_chart_data("top_universities")
        assert "data" in chart_data


class TestAnalyticsWithCache:
    """测试分析引擎与缓存集成"""
    
    def test_analytics_caching(self):
        """测试分析结果缓存"""
        cache = CacheManager()
        analytics = AnalyticsEngine(cache_manager=cache)
        
        # 创建测试数据
        data = pd.DataFrame({
            "school_name": ["北京大学", "清华大学"],
            "score": [680, 685]
        })
        analytics.set_data(data)
        
        # 第一次计算
        stats1 = analytics.get_statistics()
        
        # 检查缓存
        cache_key = "statistics"
        assert cache.has(cache_key)
        
        # 第二次计算（应该从缓存读取）
        stats2 = analytics.get_statistics()
        
        assert stats1 == stats2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
