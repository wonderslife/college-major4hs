"""
保研率数据加载器
加载保研率数据
"""

from typing import Dict, Optional
import pandas as pd
from pathlib import Path
from .base_loader import BaseLoader
from utils.logger import get_logger


class GraduateRateLoader(BaseLoader):
    """保研率数据加载器"""
    
    def __init__(self, cache_manager, file_path: str = "data/高校保研率2025.md"):
        """
        初始化加载器
        
        Args:
            cache_manager: 缓存管理器
            file_path: 保研率文件路径
        """
        super().__init__(cache_manager, file_path)
        self._school_data: Dict[str, Dict[str, any]] = {}
    
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
            # 过滤掉表头分隔行（包含多个 --- 的行）
            if '|' in line and '---' not in line:
                # 过滤掉空单元格
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
        # 清理空值
        if '院校名称' in df.columns:
            df = df.dropna(subset=['院校名称'])
            df['院校名称'] = df['院校名称'].str.strip()
        
        # 转换保研率为数字
        if '2025保研率' in df.columns:
            # 先处理特殊值，将 '---' 和空值替换为空字符串
            df['graduate_rate'] = df['2025保研率'].replace('---', '').str.replace('%', '')
            # 使用 pd.to_numeric 并设置 errors='coerce' 来处理无效值
            df['graduate_rate'] = pd.to_numeric(df['graduate_rate'], errors='coerce')
        
        # 转换保研人数为数字
        if '2025保研人数' in df.columns:
            df['graduate_count'] = pd.to_numeric(df['2025保研人数'], errors='coerce')
        
        # 构建学校数据映射
        if '院校名称' in df.columns:
            for _, row in df.iterrows():
                school_name = row['院校名称']
                
                self._school_data[school_name] = {
                    'graduate_rate': row.get('graduate_rate'),
                    'graduate_count': row.get('graduate_count'),
                    'graduate_rank': row.get('排名'),
                    'rank_change': row.get('上升/下降名次')
                }
        
        return df
    
    def get_graduate_rate(self, school_name: str) -> Optional[Dict[str, any]]:
        """
        获取学校保研率信息
        
        Args:
            school_name: 学校名称
        
        Returns:
            保研率信息字典,如果不存在则返回None
        """
        self.load()  # 确保数据已加载
        return self._school_data.get(school_name)
