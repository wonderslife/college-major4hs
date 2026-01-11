"""
数据加载器单元测试
"""
import pytest
from pathlib import Path
import pandas as pd

from core.data.base_loader import BaseLoader
from core.data.cache_manager import CacheManager


class TestCacheManager:
    """测试缓存管理器"""
    
    def test_cache_init(self):
        """测试缓存初始化"""
        cache = CacheManager()
        assert cache is not None
        assert len(cache._cache) == 0
    
    def test_cache_get_set(self):
        """测试缓存读写"""
        cache = CacheManager()
        
        # 设置缓存
        cache.set("test_key", {"data": "test_value"}, metadata={"type": "test"})
        
        # 获取缓存
        result = cache.get("test_key")
        assert result is not None
        assert result["data"] == "test_value"
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = CacheManager(maxsize=10, ttl=1)  # 1秒过期
        
        cache.set("temp_key", {"data": "temp_value"})
        
        # 立即获取应该成功
        result = cache.get("temp_key")
        assert result is not None
        
        # 等待过期后应该返回None
        import time
        time.sleep(1.1)
        result = cache.get("temp_key")
        assert result is None
    
    def test_cache_clear(self):
        """测试缓存清除"""
        cache = CacheManager()
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        
        assert len(cache._cache) == 2
        
        cache.clear()
        assert len(cache._cache) == 0
    
    def test_cache_has(self):
        """测试缓存检查"""
        cache = CacheManager()
        
        assert not cache.has("nonexistent_key")
        
        cache.set("test_key", {"data": "test_value"})
        assert cache.has("test_key")


class TestBaseLoader:
    """测试基础加载器"""
    
    def test_base_loader_init(self):
        """测试基础加载器初始化"""
        loader = BaseLoader()
        assert loader.cache_manager is not None
    
    def test_validate_dataframe_empty(self):
        """测试空DataFrame验证"""
        loader = BaseLoader()
        df = pd.DataFrame()
        is_valid = loader._validate_dataframe(df)
        assert is_valid is False
    
    def test_validate_dataframe_success(self):
        """测试有效DataFrame验证"""
        loader = BaseLoader()
        df = pd.DataFrame({
            "school_code": ["10001"],
            "school_name": ["北京大学"]
        })
        is_valid = loader._validate_dataframe(df)
        assert is_valid is True


class TestDataValidator:
    """测试数据验证器"""
    
    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        from core.data.data_validator import DataValidator
        return DataValidator()
    
    def test_validate_empty_data(self, validator):
        """测试空数据验证"""
        df = pd.DataFrame()
        result = validator.validate(df)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_missing_required_columns(self, validator):
        """测试缺少必需列的验证"""
        df = pd.DataFrame({
            "school_name": ["北京大学"]
        })
        result = validator.validate(df, required_columns=["school_code", "school_name"])
        assert result.is_valid is False
        assert any("school_code" in str(error) for error in result.errors)
    
    def test_validate_success(self, validator):
        """测试成功验证"""
        df = pd.DataFrame({
            "school_code": ["10001"],
            "school_name": ["北京大学"]
        })
        result = validator.validate(df, required_columns=["school_code", "school_name"])
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_score_range(self, validator):
        """测试分数范围验证"""
        df = pd.DataFrame({
            "score": [400, 500, 600, 750, 800]
        })
        result = validator.validate_score_range(df, "score", min_score=450, max_score=750)
        # 400和800应该被标记为无效
        assert len(result["invalid_scores"]) == 2
    
    def test_detect_duplicates(self, validator):
        """测试重复数据检测"""
        df = pd.DataFrame({
            "school_code": ["10001", "10001", "10002"],
            "major_code": ["0101", "0101", "0201"]
        })
        duplicates = validator.detect_duplicates(df, ["school_code", "major_code"])
        assert len(duplicates) == 1
    
    def test_check_data_completeness(self, validator):
        """测试数据完整性检查"""
        df = pd.DataFrame({
            "school_code": ["10001", None, "10002"],
            "school_name": ["北京大学", "清华大学", None]
        })
        result = validator.check_data_completeness(df)
        assert result["school_code"]["missing_count"] == 1
        assert result["school_name"]["missing_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
