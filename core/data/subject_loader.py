"""
学科评估数据加载器
加载学科评估数据
"""

from typing import Dict, Optional
import pandas as pd
from pathlib import Path
from .base_loader import BaseLoader
from utils.logger import get_logger


class SubjectLoader(BaseLoader):
    """学科评估数据加载器"""
    
    def __init__(self, cache_manager, file_path: str = "data/学科评估.md"):
        """
        初始化加载器
        
        Args:
            cache_manager: 缓存管理器
            file_path: 学科评估文件路径
        """
        super().__init__(cache_manager, file_path)
        self._school_subjects: Dict[str, list] = {}
        self._school_top_subjects: Dict[str, str] = {}
    
    def _load_from_file(self) -> pd.DataFrame:
        """
        从文件加载数据
        
        Returns:
            DataFrame: 原始数据
        """
        if self.file_path.suffix == '.md':
            return self._load_from_markdown()
        elif self.file_path.suffix in ['.xlsx', '.xls']:
            return pd.read_excel(self.file_path)
        else:
            raise ValueError(f"不支持的文件格式: {self.file_path.suffix}")
    
    def _load_from_markdown(self) -> pd.DataFrame:
        """从Markdown文件加载数据"""
        # 读取markdown表格
        lines = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找表格部分
        table_start = content.find('|')
        if table_start == -1:
            raise ValueError("未找到表格数据")
        
        # 解析表格
        table_lines = content[table_start:].split('\n')
        for line in table_lines:
            if '|' in line and not line.strip().startswith('|---'):
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(cells) >= 3:  # 至少要有3列
                    lines.append(cells)
        
        if not lines:
            raise ValueError("表格数据为空")
        
        # 创建DataFrame
        headers = lines[0]
        data = lines[1:]
        
        return pd.DataFrame(data, columns=headers)
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗

        Args:
            df: 原始数据

        Returns:
            DataFrame: 清洗后的数据
        """
        # 确定学校列名
        school_col = None
        for col in ['学校名称', '院校名称']:
            if col in df.columns:
                school_col = col
                break

        # 确定学科列名
        subject_col = None
        for col in ['学科名称', '一级学科名称']:
            if col in df.columns:
                subject_col = col
                break

        # 确定评估结果列名
        evaluation_col = None
        for col in ['评估结果']:
            if col in df.columns:
                evaluation_col = col
                break

        # 标准化列名
        if school_col and school_col != '学校名称':
            df['学校名称'] = df[school_col]
        if subject_col and subject_col != '学科名称':
            df['学科名称'] = df[subject_col]
        if evaluation_col and evaluation_col != '评估结果':
            df['评估结果'] = df[evaluation_col]

        # 清理空值
        if '学校名称' in df.columns:
            df = df.dropna(subset=['学校名称'])
            df['学校名称'] = df['学校名称'].str.strip()

        # 构建学校学科映射
        if '学校名称' in df.columns and '学科名称' in df.columns:
            for _, row in df.iterrows():
                school_name = row['学校名称']
                subject_name = row['学科名称']
                evaluation_result = row.get('评估结果', '')
                evaluation_batch = row.get('评估批次', '')
                subject_code = row.get('学科代码', '')

                if school_name not in self._school_subjects:
                    self._school_subjects[school_name] = []

                self._school_subjects[school_name].append({
                    '学科名称': subject_name,
                    '评估结果': evaluation_result,
                    '评估批次': evaluation_batch,
                    '学科代码': subject_code
                })

        # 获取每个学校的优势学科(排名最靠前的)
        for school_name, subjects in self._school_subjects.items():
            if subjects:
                # 简单实现:取第一个学科
                self._school_top_subjects[school_name] = subjects[0]

        return df
    
    def get_school_subjects(self, school_name: str) -> Optional[list]:
        """
        获取学校的学科列表

        Args:
            school_name: 学校名称

        Returns:
            学科列表(包含评估信息),如果不存在则返回None
        """
        self.load()  # 确保数据已加载
        return self._school_subjects.get(school_name)
    
    def get_top_subject(self, school_name: str) -> Optional[dict]:
        """
        获取学校的优势学科

        Args:
            school_name: 学校名称

        Returns:
            优势学科信息(包含评估结果),如果不存在则返回None
        """
        self.load()  # 确保数据已加载
        return self._school_top_subjects.get(school_name)
