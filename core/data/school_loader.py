"""
学校信息加载器
加载学校基本信息、属性标签等
"""

from typing import Dict, Optional
import pandas as pd
from pathlib import Path
from .base_loader import BaseLoader
from core.models.admission_data import SchoolInfo
from utils.logger import get_logger


class SchoolLoader(BaseLoader):
    """学校信息加载器"""
    
    def __init__(self, cache_manager, file_path: str = "学校信息.md"):
        """
        初始化加载器

        Args:
            cache_manager: 缓存管理器
            file_path: 学校信息文件路径
        """
        super().__init__(cache_manager, file_path)
        self._school_map: Dict[str, Dict[str, any]] = {}
    
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
                cells = [cell.strip() for cell in line.split('|')]
                # 移除首尾的空字符串
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                if len(cells) >= 2:
                    lines.append(cells)

        if not lines:
            raise ValueError("表格数据为空")

        # 创建DataFrame
        headers = lines[0]
        data = lines[1:]

        df = pd.DataFrame(data, columns=headers)

        # 重命名列以匹配 Excel 版本的列名
        column_mapping = {
            '院校名称': '学校名称',
            '所在区域': '所在区域',
            '主管部门': '主管部门',
            '办学层次': '办学层次',
            '双一流': '双一流',
            '985': '985',
            '民办高校': '民办高校',
            '独立学院': '独立学院'
        }
        df = df.rename(columns=column_mapping)

        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            df: 原始数据
        
        Returns:
            DataFrame: 清洗后的数据
        """
        # 清理空值
        df = df.dropna(subset=['学校名称'])
        
        # 清理字符串
        df['学校名称'] = df['学校名称'].str.strip()
        
        # 构建学校信息映射
        for _, row in df.iterrows():
            school_name = row.get('学校名称', '')
            if not school_name:
                continue

            self._school_map[school_name] = {
                'school_code': row.get('院校编码', ''),
                'region': row.get('所在区域', ''),
                'authority': row.get('主管部门', ''),
                'level': row.get('办学层次', ''),
                'is_double_first_class': self._to_bool(row.get('双一流', '')),
                'is_985': self._to_bool(row.get('985', '')),
                'is_private': self._to_bool(row.get('民办高校', '')),
                'is_independent': self._to_bool(row.get('独立学院', ''))
            }
        
        return df
    
    def _extract_province(self, region: str) -> Optional[str]:
        """从区域字符串中提取省份"""
        if not region or pd.isna(region):
            return None
        
        # 简单实现:取第一个词
        parts = str(region).split()
        return parts[0] if parts else None
    
    def _extract_city(self, region: str) -> Optional[str]:
        """从区域字符串中提取城市"""
        if not region or pd.isna(region):
            return None
        
        # 简单实现:取第二个词
        parts = str(region).split()
        return parts[1] if len(parts) > 1 else None
    
    def _to_bool(self, value: any) -> bool:
        """转换为布尔值"""
        if pd.isna(value):
            return False
        return str(value).strip().upper() in ['Y', 'YES', 'TRUE', '是']
    
    def get_school_info(self, school_name: str) -> Optional[Dict[str, any]]:
        """
        获取学校信息
        
        Args:
            school_name: 学校名称
        
        Returns:
            学校信息字典,如果不存在则返回None
        """
        self.load()  # 确保数据已加载
        return self._school_map.get(school_name)
    
    def get_all_school_names(self) -> list:
        """获取所有学校名称"""
        self.load()  # 确保数据已加载
        return list(self._school_map.keys())
    
    def to_school_info_model(self, school_name: str) -> Optional[SchoolInfo]:
        """
        转换为SchoolInfo模型
        
        Args:
            school_name: 学校名称
        
        Returns:
            SchoolInfo模型实例
        """
        info = self.get_school_info(school_name)
        if info is None:
            return None
        
        return SchoolInfo(
            school_code=info.get('school_code', ''),
            school_name=school_name,
            province=info.get('province'),
            city=info.get('city'),
            authority=info.get('authority'),
            is_985=info.get('is_985', False),
            is_211=info.get('is_211', False),
            is_double_first_class=info.get('is_double_first_class', False),
            is_private=info.get('is_private', False),
            is_independent=info.get('is_independent', False)
        )
