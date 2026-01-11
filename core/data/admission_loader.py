"""
专业投档数据加载器
加载2023-2025年的专业投档数据
"""

from typing import Dict, Optional
import pandas as pd
from pathlib import Path
from .base_loader import BaseLoader
from utils.logger import get_logger


class AdmissionLoader(BaseLoader):
    """专业投档数据加载器"""
    
    # 三年数据的列名映射（不重命名，保持原始列名）
    COLUMN_MAPPINGS = {
        2023: {
            '投档位次': '位次'
        },
        2024: {
            '投档位次': '位次'
        },
        2025: {
            '投档位次': '位次'
        }
    }
    
    # 统一列名（保持原始中文列名）
    UNIFIED_COLUMNS = [
        '院校编号', '学校名称', '院校名称', '专业编号',
        '招生专业', '专业名称', '投档最低分', '位次', '投档位次'
    ]
    
    def __init__(self, cache_manager, year: int, file_path: str):
        """
        初始化加载器
        
        Args:
            cache_manager: 缓存管理器
            year: 年份(2023/2024/2025)
            file_path: 数据文件路径
        """
        if year not in [2023, 2024, 2025]:
            raise ValueError(f"年份必须是2023/2024/2025, 当前: {year}")
        
        self.year = year
        super().__init__(cache_manager, file_path)
    
    def _generate_cache_key(self) -> str:
        """生成缓存键"""
        return f"admission_{self.year}_{self.file_path.name}"
    
    def _load_from_file(self) -> pd.DataFrame:
        """
        从文件加载数据
        
        Returns:
            DataFrame: 原始数据
        """
        if self.file_path.suffix == '.md':
            return self._load_from_markdown()
        elif self.file_path.suffix in ['.xlsx', '.xls']:
            return self._load_from_excel()
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
                # 不去除空格，保留原始列结构
                cells = [cell.strip() for cell in line.split('|')]
                # 移除首尾的空字符串（由开头的|和结尾的|导致）
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                if len(cells) >= 6:  # 6列: 院校编号|院校名称|专业编号|招生专业|投档最低分|投档位次
                    lines.append(cells)

        if not lines:
            raise ValueError("表格数据为空")

        # 创建DataFrame
        headers = lines[0]
        data = lines[1:]

        df = pd.DataFrame(data, columns=headers)

        # 应用列名映射
        mapping = self.COLUMN_MAPPINGS[self.year]
        df = df.rename(columns=mapping)

        # 检查第一行是否是分隔符行（包含 '---'）
        if not df.empty:
            first_row = df.iloc[0]
            if any('---' in str(cell) for cell in first_row):
                df = df.iloc[1:].reset_index(drop=True)

        return df
    
    def _load_from_excel(self) -> pd.DataFrame:
        """从Excel文件加载数据"""
        df = pd.read_excel(self.file_path)
        
        # 应用列名映射
        mapping = self.COLUMN_MAPPINGS[self.year]
        df = df.rename(columns=mapping)
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗

        Args:
            df: 原始数据

        Returns:
            DataFrame: 清洗后的数据
        """
        # 添加年份列
        df['year'] = self.year

        # 清洗分数
        if '投档最低分' in df.columns:
            df['投档最低分'] = pd.to_numeric(df['投档最低分'], errors='coerce')

        # 清洗位次（处理不同年份的列名）
        if '位次' in df.columns:
            df['位次'] = pd.to_numeric(df['位次'], errors='coerce')
        elif '投档位次' in df.columns:
            df['位次'] = pd.to_numeric(df['投档位次'], errors='coerce')

        # 确定院校列名
        school_col = None
        if '招生院校' in df.columns:
            school_col = '招生院校'
        elif '院校名称' in df.columns:
            school_col = '院校名称'
        elif '学校名称' in df.columns:
            school_col = '学校名称'

        # 确定专业列名
        major_col = None
        if '招生专业' in df.columns:
            major_col = '招生专业'
        elif '专业名称' in df.columns:
            major_col = '专业名称'

        # 清理空值
        if school_col and major_col:
            df = df.dropna(subset=[school_col, major_col])

            # 清理字符串
            df[school_col] = df[school_col].str.strip()
            df[major_col] = df[major_col].str.strip()

        return df


class MultiYearAdmissionLoader:
    """多年份投档数据加载器"""
    
    def __init__(self, cache_manager):
        """
        初始化多年份加载器
        
        Args:
            cache_manager: 缓存管理器
        """
        self.cache_manager = cache_manager
        self.loaders: Dict[int, AdmissionLoader] = {}
        self.logger = get_logger("MultiYearAdmissionLoader")
    
    def add_year(self, year: int, file_path: str) -> None:
        """
        添加年份加载器
        
        Args:
            year: 年份
            file_path: 数据文件路径
        """
        loader = AdmissionLoader(self.cache_manager, year, file_path)
        self.loaders[year] = loader
        self.logger.info(f"添加年份加载器: {year}")
    
    def load_all_years(self, force_reload: bool = False) -> Dict[int, pd.DataFrame]:
        """
        加载所有年份数据
        
        Args:
            force_reload: 是否强制重新加载
        
        Returns:
            Dict[int, DataFrame]: 年份到数据的映射
        """
        result = {}
        for year, loader in self.loaders.items():
            result[year] = loader.load(force_reload)
        
        return result
    
    def load_year(self, year: int, force_reload: bool = False) -> Optional[pd.DataFrame]:
        """
        加载指定年份数据
        
        Args:
            year: 年份
            force_reload: 是否强制重新加载
        
        Returns:
            DataFrame: 数据,如果年份不存在则返回None
        """
        if year not in self.loaders:
            return None
        return self.loaders[year].load(force_reload)
    
    def get_data_2023(self) -> Optional[pd.DataFrame]:
        """获取2023年数据"""
        return self.load_year(2023)
    
    def get_data_2024(self) -> Optional[pd.DataFrame]:
        """获取2024年数据"""
        return self.load_year(2024)
    
    def get_data_2025(self) -> Optional[pd.DataFrame]:
        """获取2025年数据"""
        return self.load_year(2025)
