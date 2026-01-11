"""
招生数据模型
定义系统使用的数据结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class SchoolInfo(BaseModel):
    """院校信息模型"""
    
    school_code: str = Field(..., description="院校编码,4位数字")
    school_name: str = Field(..., description="院校名称")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    authority: Optional[str] = Field(None, description="办学性质")
    is_985: bool = Field(default=False, description="是否985")
    is_211: bool = Field(default=False, description="是否211")
    is_double_first_class: bool = Field(default=False, description="是否双一流")
    is_private: bool = Field(default=False, description="是否民办")
    is_independent: bool = Field(default=False, description="是否独立学院")
    graduate_rate: Optional[float] = Field(None, ge=0, le=100, description="保研率(%)")
    graduate_rank: Optional[int] = Field(None, ge=1, description="保研率排名")
    graduate_count: Optional[int] = Field(None, ge=0, description="保研人数")
    graduate_rank_change: Optional[str] = Field(None, description="保研率排名变化(+N/-N/0/)")
    
    @validator('school_code')
    def validate_school_code(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError('院校编码必须是4位数字')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_code": "0378",
                "school_name": "安徽财经大学",
                "province": "安徽",
                "city": "蚌埠",
                "authority": "公办",
                "is_985": False,
                "is_211": False,
                "is_double_first_class": False,
                "is_private": False,
                "is_independent": False,
                "graduate_rate": None,
                "graduate_rank": None,
                "graduate_count": None,
                "graduate_rank_change": None
            }
        }


class MajorAdmission(BaseModel):
    """专业投档记录模型"""
    
    school_code: str = Field(..., description="院校编码")
    school_name: str = Field(..., description="院校名称")
    major_code: str = Field(..., description="专业编号")
    major_name: str = Field(..., description="专业名称")
    year: int = Field(..., ge=2023, le=2025, description="年份")
    score: Optional[int] = Field(None, ge=0, le=750, description="投档分数")
    rank: Optional[int] = Field(None, ge=1, description="投档位次")
    
    @validator('school_code')
    def validate_school_code(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError('院校编码必须是4位数字')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_code": "0378",
                "school_name": "安徽财经大学",
                "major_code": "01",
                "major_name": "经济学类(经济学、国民经济管理)",
                "year": 2025,
                "score": 561,
                "rank": 27324
            }
        }


class ComprehensiveRecord(BaseModel):
    """综合记录模型(大宽表)"""
    
    # 基础标识
    school_code: str = Field(..., description="院校编码")
    school_name: str = Field(..., description="院校名称")
    major_code: str = Field(..., description="专业编号")
    major_name: str = Field(..., description="专业名称")
    
    # 院校属性
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    authority: Optional[str] = Field(None, description="办学性质")
    is_985: bool = False
    is_211: bool = False
    is_double_first_class: bool = False
    is_private: bool = False
    is_independent: bool = False
    graduate_rate: Optional[float] = None
    graduate_rank: Optional[int] = None
    graduate_count: Optional[int] = None
    graduate_rank_change: Optional[str] = None
    top_subject: Optional[str] = None
    
    # 三年投档数据
    score_2023: Optional[int] = Field(None, description="2023年投档分数")
    rank_2023: Optional[int] = Field(None, description="2023年投档位次")
    score_2024: Optional[int] = Field(None, description="2024年投档分数")
    rank_2024: Optional[int] = Field(None, description="2024年投档位次")
    score_2025: Optional[int] = Field(None, description="2025年投档分数")
    rank_2025: Optional[int] = Field(None, description="2025年投档位次")
    
    # 趋势分析
    score_trend: Optional[str] = Field(None, description="分数趋势(上升/下降/稳定)")
    score_change: Optional[int] = Field(None, description="分数变化(2025-2023)")
    rank_change: Optional[int] = Field(None, description="位次变化(2025-2023)")
    has_three_years: bool = Field(False, description="是否有三年数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_code": "0378",
                "school_name": "安徽财经大学",
                "major_code": "01",
                "major_name": "经济学类(经济学、国民经济管理)",
                "province": "安徽",
                "city": None,
                "authority": None,
                "is_985": False,
                "is_211": False,
                "is_double_first_class": False,
                "is_private": False,
                "is_independent": False,
                "graduate_rate": None,
                "graduate_rank": None,
                "graduate_count": None,
                "graduate_rank_change": None,
                "top_subject": None,
                "score_2023": 561,
                "rank_2023": 27324,
                "score_2024": 561,
                "rank_2024": 27324,
                "score_2025": 561,
                "rank_2025": 27324,
                "score_trend": "稳定",
                "score_change": 0,
                "rank_change": 0,
                "has_three_years": True
            }
        }


class DataValidationReport(BaseModel):
    """数据验证报告"""
    
    total_records: int = Field(..., description="总记录数")
    valid_records: int = Field(..., description="有效记录数")
    invalid_records: int = Field(..., description="无效记录数")
    validation_rate: float = Field(..., description="验证通过率(%)")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告列表")
    validation_time: datetime = Field(default_factory=datetime.now, description="验证时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 1000,
                "valid_records": 950,
                "invalid_records": 50,
                "validation_rate": 95.0,
                "errors": [],
                "warnings": []
            }
        }
