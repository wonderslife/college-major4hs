"""
分析引擎单元测试
"""
import pytest
import pandas as pd
from core.analytics.analytics import AnalyticsEngine
from core.analytics.statistics import StatisticsEngine
from core.analytics.search import SearchEngine
from core.analytics.probability import ProbabilityCalculator


class TestAnalyticsEngine:
    """测试分析引擎"""
    
    @pytest.fixture
    def analytics_engine(self):
        """创建分析引擎实例"""
        return AnalyticsEngine()
    
    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        return pd.DataFrame({
            "school_code": ["10001", "10001", "10002", "10002"],
            "school_name": ["北京大学", "北京大学", "清华大学", "清华大学"],
            "major_code": ["0101", "0201", "0301", "0401"],
            "major_name": ["哲学", "经济学", "数学", "物理"],
            "score": [680, 690, 685, 675],
            "rank": [100, 50, 80, 120],
            "year": [2025, 2025, 2025, 2025]
        })
    
    def test_analytics_engine_init(self, analytics_engine):
        """测试分析引擎初始化"""
        assert analytics_engine is not None
        assert analytics_engine.stats_engine is not None
        assert analytics_engine.search_engine is not None
        assert analytics_engine.probability_calculator is not None
    
    def test_set_data(self, analytics_engine, sample_data):
        """测试设置数据"""
        analytics_engine.set_data(sample_data)
        assert len(analytics_engine.data) == 4
    
    def test_get_statistics(self, analytics_engine, sample_data):
        """测试获取统计数据"""
        analytics_engine.set_data(sample_data)
        stats = analytics_engine.get_statistics()
        
        assert "total_records" in stats
        assert stats["total_records"] == 4
        assert "score_range" in stats
        assert "rank_range" in stats


class TestStatisticsEngine:
    """测试统计引擎"""
    
    @pytest.fixture
    def stats_engine(self):
        """创建统计引擎实例"""
        return StatisticsEngine()
    
    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        return pd.DataFrame({
            "score": [600, 650, 700, 680, 720],
            "rank": [5000, 4000, 2000, 2500, 1000]
        })
    
    def test_calculate_score_distribution(self, stats_engine, sample_data):
        """测试分数分布计算"""
        result = stats_engine.calculate_score_distribution(sample_data)
        
        assert "bins" in result
        assert "counts" in result
        assert len(result["bins"]) > 0
    
    def test_calculate_rank_distribution(self, stats_engine, sample_data):
        """测试位次分布计算"""
        result = stats_engine.calculate_rank_distribution(sample_data)
        
        assert "bins" in result
        assert "counts" in result
    
    def test_calculate_statistics(self, stats_engine, sample_data):
        """测试基本统计"""
        result = stats_engine.calculate_statistics(sample_data, "score")
        
        assert "mean" in result
        assert "median" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
    
    def test_get_top_universities(self, stats_engine):
        """测试获取热门院校"""
        data = pd.DataFrame({
            "school_name": ["北京大学", "清华大学", "北京大学", "清华大学", "北京大学"],
            "score": [680, 685, 690, 675, 670]
        })
        result = stats_engine.get_top_universities(data, limit=2)
        
        assert len(result) <= 2
        assert "school_name" in result.columns
        assert "count" in result.columns


class TestSearchEngine:
    """测试搜索引擎"""
    
    @pytest.fixture
    def search_engine(self):
        """创建搜索引擎实例"""
        return SearchEngine()
    
    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        return pd.DataFrame({
            "school_name": ["北京大学", "清华大学", "北京大学医学部", "北京大学元培学院"],
            "major_name": ["哲学", "数学", "临床医学", "通识教育"],
            "province": ["北京市", "北京市", "北京市", "北京市"],
            "score": [680, 685, 690, 675],
            "rank": [100, 80, 50, 120]
        })
    
    def test_search_by_keyword(self, search_engine, sample_data):
        """测试关键词搜索"""
        result = search_engine.search_by_keyword(sample_data, "北京大学")
        
        assert len(result) > 0
        assert all("北京大学" in row["school_name"] for _, row in result.iterrows())
    
    def test_search_by_score_range(self, search_engine, sample_data):
        """测试分数范围搜索"""
        result = search_engine.search_by_score_range(sample_data, 675, 685)
        
        assert len(result) > 0
        assert all(675 <= score <= 685 for score in result["score"])
    
    def test_search_by_rank_range(self, search_engine, sample_data):
        """测试位次范围搜索"""
        result = search_engine.search_by_rank_range(sample_data, 50, 100)
        
        assert len(result) > 0
        assert all(50 <= rank <= 100 for rank in result["rank"])
    
    def test_advanced_search(self, search_engine, sample_data):
        """测试高级搜索"""
        result = search_engine.advanced_search(
            sample_data,
            keyword="北京",
            min_score=680,
            max_rank=100
        )
        
        assert len(result) > 0
        assert all("北京" in row["school_name"] for _, row in result.iterrows())
        assert all(score >= 680 for score in result["score"])
        assert all(rank <= 100 for rank in result["rank"])


class TestProbabilityCalculator:
    """测试概率计算器"""
    
    @pytest.fixture
    def calculator(self):
        """创建概率计算器实例"""
        return ProbabilityCalculator()
    
    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        return pd.DataFrame({
            "school_name": ["北京大学", "北京大学", "北京大学", "清华大学", "清华大学"],
            "major_name": ["哲学", "经济学", "数学", "物理", "化学"],
            "score_2023": [675, 685, 690, 680, 670],
            "rank_2023": [120, 80, 50, 100, 130],
            "score_2024": [680, 690, 695, 685, 675],
            "rank_2024": [110, 70, 45, 90, 120],
            "score_2025": [685, 695, 700, 690, 680],
            "rank_2025": [100, 60, 40, 80, 110]
        })
    
    def test_calculate_admission_probability(self, calculator, sample_data):
        """测试录取概率计算"""
        # 查找北京大学哲学专业
        major_data = sample_data[
            (sample_data["school_name"] == "北京大学") &
            (sample_data["major_name"] == "哲学")
        ]
        
        result = calculator.calculate_admission_probability(
            major_data,
            user_score=682,
            user_rank=105
        )
        
        assert "probability" in result
        assert "level" in result
        assert 0 <= result["probability"] <= 100
    
    def test_batch_calculate_probability(self, calculator, sample_data):
        """测试批量概率计算"""
        results = calculator.batch_calculate_probability(
            sample_data,
            user_score=685,
            user_rank=90
        )
        
        assert len(results) > 0
        assert all("probability" in result for result in results)
        assert all("level" in result for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
