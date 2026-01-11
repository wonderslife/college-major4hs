"""
数据加载集成测试
"""
import pytest
import pandas as pd
from pathlib import Path

from core.data.cache_manager import CacheManager
from core.data.cache_invalidator import CacheInvalidator
from core.data.data_validator import DataValidator


class TestDataLoadingIntegration:
    """测试数据加载集成"""
    
    @pytest.fixture
    def cache_dir(self, tmp_path):
        """临时缓存目录"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
    
    def test_cache_with_invalidator(self, cache_dir):
        """测试缓存和失效器集成"""
        cache = CacheManager(cache_dir=str(cache_dir))
        invalidator = CacheInvalidator(cache)
        
        # 设置缓存
        cache.set("test_key", {"data": "test_value"}, metadata={"file_path": "test.md"})
        
        # 验证缓存存在
        assert cache.has("test_key")
        
        # 模拟文件修改
        test_file = cache_dir / "test.md"
        test_file.write_text("test content")
        
        # 检查是否需要失效
        should_invalidate = invalidator.should_invalidate("test_key", str(test_file))
        assert should_invalidate is False  # 刚创建，不需要失效
    
    def test_data_validator_with_cache(self):
        """测试数据验证器和缓存集成"""
        validator = DataValidator()
        cache = CacheManager()
        
        # 创建测试数据
        df = pd.DataFrame({
            "school_code": ["10001", "10002"],
            "school_name": ["北京大学", "清华大学"],
            "score": [680, 685]
        })
        
        # 验证数据
        result = validator.validate(df, required_columns=["school_code", "school_name"])
        assert result.is_valid is True
        
        # 缓存验证后的数据
        cache.set("validated_data", df.to_dict("records"))
        assert cache.has("validated_data")
    
    def test_multi_year_data_validation(self):
        """测试多年数据验证"""
        validator = DataValidator()
        
        # 创建多年数据
        df_2023 = pd.DataFrame({
            "school_code": ["10001"],
            "score_2023": [675],
            "rank_2023": [120]
        })
        
        df_2024 = pd.DataFrame({
            "school_code": ["10001"],
            "score_2024": [680],
            "rank_2024": [110]
        })
        
        # 合并数据
        df_combined = pd.merge(df_2023, df_2024, on="school_code")
        
        # 验证合并后的数据
        result = validator.validate_trend_data(df_combined)
        assert result["is_valid"]
    
    def test_data_quality_scoring(self):
        """测试数据质量评分"""
        validator = DataValidator()
        
        # 创建高质量数据
        df = pd.DataFrame({
            "school_code": ["10001", "10002", "10003"],
            "school_name": ["北京大学", "清华大学", "复旦大学"],
            "score": [680, 685, 675],
            "rank": [100, 80, 120]
        })
        
        result = validator.check_data_completeness(df)
        score = validator.calculate_quality_score(df, result)
        
        assert score > 0
        assert score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
