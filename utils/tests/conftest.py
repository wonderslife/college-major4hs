"""
测试配置和共享fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_data_dir():
    """获取测试数据目录"""
    return project_root / "data"


@pytest.fixture
def cache_dir():
    """获取缓存目录"""
    return project_root / "cache"


@pytest.fixture
def sample_admission_data():
    """示例投档数据"""
    return [
        {
            "school_code": "10001",
            "school_name": "北京大学",
            "major_code": "0101",
            "major_name": "哲学",
            "province": "北京市",
            "score": 680,
            "rank": 100,
            "year": 2025
        },
        {
            "school_code": "10001",
            "school_name": "北京大学",
            "major_code": "0201",
            "major_name": "经济学",
            "province": "北京市",
            "score": 690,
            "rank": 50,
            "year": 2025
        }
    ]


@pytest.fixture
def sample_school_data():
    """示例学校数据"""
    return {
        "school_code": "10001",
        "school_name": "北京大学",
        "province": "北京市",
        "city": "北京市",
        "authority": "教育部",
        "is_985": True,
        "is_211": True,
        "is_double_first_class": True
    }
