"""
数据验证工具模块
"""

from typing import Tuple, Optional


def validate_score(score: int, min_score: int = 0, max_score: int = 750) -> Tuple[bool, Optional[str]]:
    """
    验证分数是否有效
    
    Args:
        score: 要验证的分数
        min_score: 最小分数
        max_score: 最大分数
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(score, (int, float)):
        return False, "分数必须是数字"
    
    if score < min_score or score > max_score:
        return False, f"分数必须在{min_score}-{max_score}之间"
    
    return True, None


def validate_rank(rank: int, min_rank: int = 1, max_rank: int = 1000000) -> Tuple[bool, Optional[str]]:
    """
    验证位次是否有效
    
    Args:
        rank: 要验证的位次
        min_rank: 最小位次
        max_rank: 最大位次
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(rank, int):
        return False, "位次必须是整数"
    
    if rank < min_rank or rank > max_rank:
        return False, f"位次必须在{min_rank}-{max_rank}之间"
    
    return True, None


def validate_school_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    验证院校编码是否有效
    
    Args:
        code: 院校编码
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(code, str):
        return False, "院校编码必须是字符串"
    
    if not code.isdigit() or len(code) != 4:
        return False, "院校编码必须是4位数字"
    
    return True, None


def validate_graduate_rate(rate: float) -> Tuple[bool, Optional[str]]:
    """
    验证保研率是否有效
    
    Args:
        rate: 保研率
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not isinstance(rate, (int, float)):
        return False, "保研率必须是数字"
    
    if rate < 0 or rate > 100:
        return False, "保研率必须在0-100之间"
    
    return True, None
