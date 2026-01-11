"""
路由层模块
"""

from .data_bp import data_bp
from .history_bp import history_bp
from .prediction_bp import prediction_bp
from .export_bp import export_bp

__all__ = [
    "data_bp",
    "history_bp",
    "prediction_bp",
    "export_bp"
]
