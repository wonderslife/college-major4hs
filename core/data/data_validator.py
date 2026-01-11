"""
数据验证器
验证数据质量,生成验证报告
"""

import pandas as pd
from typing import Dict, Any, List
from core.models.admission_data import DataValidationReport
from utils.logger import get_logger


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        """初始化数据验证器"""
        self.logger = get_logger("DataValidator")
    
    def validate_admission_data(self, df: pd.DataFrame) -> DataValidationReport:
        """
        验证投档数据
        
        Args:
            df: 投档数据
        
        Returns:
            数据验证报告
        """
        errors = []
        warnings = []
        
        # 检查必需列
        required_columns = ['school_code', 'school_name', 'major_name']
        for col in required_columns:
            if col not in df.columns:
                errors.append({
                    'type': 'missing_column',
                    'column': col,
                    'message': f'缺少必需列: {col}'
                })
        
        # 检查空值
        if 'school_name' in df.columns:
            null_count = df['school_name'].isna().sum()
            if null_count > 0:
                warnings.append({
                    'type': 'null_values',
                    'column': 'school_name',
                    'count': int(null_count),
                    'message': f'school_name列有{null_count}条空值'
                })
        
        # 检查院校编码格式
        if 'school_code' in df.columns:
            invalid_codes = df[df['school_code'].str.len() != 4]
            if len(invalid_codes) > 0:
                warnings.append({
                    'type': 'invalid_format',
                    'column': 'school_code',
                    'count': len(invalid_codes),
                    'message': f'school_code有{len(invalid_codes)}条格式不正确(应为4位数字)'
                })
        
        # 检查分数范围
        for year in [2023, 2024, 2025]:
            score_col = f'score_{year}'
            if score_col in df.columns:
                invalid_scores = df[(df[score_col] < 0) | (df[score_col] > 750)]
                if len(invalid_scores) > 0:
                    errors.append({
                        'type': 'invalid_range',
                        'column': score_col,
                        'count': len(invalid_scores),
                        'message': f'{score_col}有{len(invalid_scores)}条分数超出范围(0-750)'
                    })
        
        # 检查位次
        for year in [2023, 2024, 2025]:
            rank_col = f'rank_{year}'
            if rank_col in df.columns:
                invalid_ranks = df[df[rank_col] < 0]
                if len(invalid_ranks) > 0:
                    errors.append({
                        'type': 'invalid_value',
                        'column': rank_col,
                        'count': len(invalid_ranks),
                        'message': f'{rank_col}有{len(invalid_ranks)}条负值'
                    })
        
        # 检查保研率
        if 'graduate_rate' in df.columns:
            invalid_rates = df[(df['graduate_rate'] < 0) | (df['graduate_rate'] > 100)]
            if len(invalid_rates) > 0:
                errors.append({
                    'type': 'invalid_range',
                    'column': 'graduate_rate',
                    'count': len(invalid_rates),
                    'message': f'graduate_rate有{len(invalid_rates)}条超出范围(0-100)'
                })
        
        # 计算统计
        total_records = len(df)
        valid_records = total_records - sum(error['count'] for error in errors if 'count' in error)
        invalid_records = total_records - valid_records
        validation_rate = (valid_records / total_records * 100) if total_records > 0 else 0
        
        return DataValidationReport(
            total_records=total_records,
            valid_records=int(valid_records),
            invalid_records=int(invalid_records),
            validation_rate=round(validation_rate, 2),
            errors=errors,
            warnings=warnings
        )
    
    def validate_wide_table(self, df: pd.DataFrame) -> DataValidationReport:
        """
        验证宽表数据
        
        Args:
            df: 宽表数据
        
        Returns:
            数据验证报告
        """
        errors = []
        warnings = []
        
        # 检查必需列
        required_columns = [
            'school_code', 'school_name', 'major_code', 'major_name',
            'score_2023', 'score_2024', 'score_2025'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                errors.append({
                    'type': 'missing_column',
                    'column': col,
                    'message': f'缺少必需列: {col}'
                })
        
        # 检查数据完整性
        total_records = len(df)
        if total_records == 0:
            errors.append({
                'type': 'empty_data',
                'message': '宽表为空'
            })
            return DataValidationReport(
                total_records=0,
                valid_records=0,
                invalid_records=0,
                validation_rate=0,
                errors=errors,
                warnings=warnings
            )
        
        # 检查三年数据覆盖率
        has_three_years = df['has_three_years'].sum() if 'has_three_years' in df.columns else 0
        coverage_rate = (has_three_years / total_records * 100) if total_records > 0 else 0
        
        if coverage_rate < 50:
            warnings.append({
                'type': 'low_coverage',
                'message': f'三年数据覆盖率较低: {coverage_rate:.2f}%'
            })
        
        # 检查重复记录
        if 'school_name' in df.columns and 'major_name' in df.columns:
            duplicates = df.duplicated(subset=['school_name', 'major_name']).sum()
            if duplicates > 0:
                warnings.append({
                    'type': 'duplicate_records',
                    'count': int(duplicates),
                    'message': f'发现{duplicates}条重复记录'
                })
        
        # 检查学校信息完整性
        if 'province' in df.columns:
            missing_province = df['province'].isna().sum()
            if missing_province > total_records * 0.5:
                warnings.append({
                    'type': 'missing_data',
                    'column': 'province',
                    'message': f'省份信息缺失较多: {missing_province}条'
                })
        
        # 计算统计
        valid_records = total_records - len(errors)
        validation_rate = (valid_records / total_records * 100) if total_records > 0 else 0
        
        return DataValidationReport(
            total_records=total_records,
            valid_records=int(valid_records),
            invalid_records=len(errors),
            validation_rate=round(validation_rate, 2),
            errors=errors,
            warnings=warnings
        )
    
    def generate_validation_summary(self, report: DataValidationReport) -> Dict[str, Any]:
        """
        生成验证摘要
        
        Args:
            report: 验证报告
        
        Returns:
            验证摘要
        """
        summary = {
            'status': 'PASS' if report.validation_rate >= 90 else 'WARNING' if report.validation_rate >= 70 else 'FAIL',
            'validation_rate': report.validation_rate,
            'total_records': report.total_records,
            'error_count': len(report.errors),
            'warning_count': len(report.warnings),
            'critical_issues': [
                error for error in report.errors 
                if error['type'] in ['missing_column', 'invalid_range', 'empty_data']
            ]
        }
        
        return summary
