"""
图表渲染器
生成各种图表的JSON配置
"""

import json
from typing import Dict, Any, List
from utils.logger import get_logger


class ChartRenderer:
    """图表渲染器"""

    def __init__(self):
        """初始化图表渲染器"""
        self.logger = get_logger("ChartRenderer")

    def generate_chart(self, chart_type: str, data: Any) -> str:
        """
        生成图表

        Args:
            chart_type: 图表类型
            data: 图表数据

        Returns:
            图表JSON配置
        """
        try:
            if chart_type == 'score_distribution':
                return self.generate_score_distribution_chart(data)
            elif chart_type == 'rank_distribution':
                return self.generate_rank_distribution_chart(data)
            elif chart_type == 'top_universities':
                return self.generate_top_universities_chart(data)
            elif chart_type == 'top_majors':
                return self.generate_top_majors_chart(data)
            else:
                self.logger.warning(f"未知的图表类型: {chart_type}")
                return json.dumps({})
        except Exception as e:
            self.logger.error(f"生成图表失败: {e}")
            return json.dumps({})

    def generate_score_distribution_chart(self, data: Dict[str, Any]) -> str:
        """
        生成分数分布柱状图

        Args:
            data: 分数分布数据

        Returns:
            图表JSON配置
        """
        ranges = data.get('ranges', [])
        scores = data.get('scores', [])

        labels = [f"{r['min']}-{r['max']}" for r in ranges]

        chart_data = [{
            'x': labels,
            'y': scores,
            'type': 'bar',
            'marker': {
                'color': 'rgba(102, 126, 234, 0.8)',
                'line': {
                    'color': 'rgba(102, 126, 234, 1.0)',
                    'width': 1
                }
            }
        }]

        layout = {
            'title': '分数分布',
            'xaxis': {'title': '分数段'},
            'yaxis': {'title': '数量'},
            'margin': {'l': 50, 'r': 20, 't': 50, 'b': 60}
        }

        return json.dumps(chart_data)

    def generate_rank_distribution_chart(self, data: Dict[str, Any]) -> str:
        """
        生成位次分布柱状图

        Args:
            data: 位次分布数据

        Returns:
            图表JSON配置
        """
        ranges = data.get('ranges', [])
        counts = data.get('counts', [])

        labels = [f"{r['min']}-{r['max']}" for r in ranges]

        chart_data = [{
            'x': labels,
            'y': counts,
            'type': 'bar',
            'marker': {
                'color': 'rgba(240, 147, 251, 0.8)',
                'line': {
                    'color': 'rgba(240, 147, 251, 1.0)',
                    'width': 1
                }
            }
        }]

        layout = {
            'title': '位次分布',
            'xaxis': {'title': '位次段'},
            'yaxis': {'title': '数量'},
            'margin': {'l': 50, 'r': 20, 't': 50, 'b': 60}
        }

        return json.dumps(chart_data)

    def generate_top_universities_chart(self, data: List[Dict[str, Any]]) -> str:
        """
        生成热门院校排行柱状图

        Args:
            data: 院校数据列表

        Returns:
            图表JSON配置
        """
        if not data:
            # 返回空图表
            return json.dumps([])

        names = [item.get('name', '') for item in data]
        avg_scores = [item.get('avg_score', 0) for item in data]

        chart_data = [{
            'x': names,
            'y': avg_scores,
            'type': 'bar',
            'marker': {
                'color': 'rgba(79, 172, 254, 0.8)',
                'line': {
                    'color': 'rgba(79, 172, 254, 1.0)',
                    'width': 1
                }
            },
            'orientation': 'v'
        }]

        layout = {
            'title': '热门院校排行（按平均分）',
            'xaxis': {'title': '院校名称', 'tickangle': -45},
            'yaxis': {'title': '平均分'},
            'margin': {'l': 50, 'r': 20, 't': 50, 'b': 100}
        }

        return json.dumps(chart_data)

    def generate_top_majors_chart(self, data: List[Dict[str, Any]]) -> str:
        """
        生成热门专业排行柱状图

        Args:
            data: 专业数据列表

        Returns:
            图表JSON配置
        """
        if not data:
            # 返回空图表
            return json.dumps([])

        names = [item.get('name', '') for item in data]
        avg_scores = [item.get('avg_score', 0) for item in data]

        chart_data = [{
            'x': names,
            'y': avg_scores,
            'type': 'bar',
            'marker': {
                'color': 'rgba(67, 233, 123, 0.8)',
                'line': {
                    'color': 'rgba(67, 233, 123, 1.0)',
                    'width': 1
                }
            },
            'orientation': 'v'
        }]

        layout = {
            'title': '热门专业排行（按平均分）',
            'xaxis': {'title': '专业名称', 'tickangle': -45},
            'yaxis': {'title': '平均分'},
            'margin': {'l': 50, 'r': 20, 't': 50, 'b': 100}
        }

        return json.dumps(chart_data)

    def generate_radar_chart(self, data: Dict[str, Any]) -> str:
        """
        生成分数分布雷达图

        Args:
            data: 基础统计数据

        Returns:
            图表JSON配置
        """
        score_range = data.get('score_range', {})
        min_score = score_range.get('min', 0)
        max_score = score_range.get('max', 0)
        mean_score = score_range.get('mean', 0)
        median_score = score_range.get('median', 0)

        # 归一化到0-100
        if max_score > 0:
            min_norm = (min_score / max_score) * 100
            max_norm = 100
            mean_norm = (mean_score / max_score) * 100
            median_norm = (median_score / max_score) * 100
        else:
            min_norm = 0
            max_norm = 100
            mean_norm = 50
            median_norm = 50

        chart_data = [{
            'type': 'scatterpolar',
            'r': [min_norm, max_norm, mean_norm, median_norm],
            'theta': ['最低分', '最高分', '平均分', '中位数'],
            'fill': 'toself',
            'name': '分数分布',
            'marker': {
                'color': 'rgba(102, 126, 234, 0.8)',
                'line': {
                    'color': 'rgba(102, 126, 234, 1.0)',
                    'width': 2
                }
            }
        }]

        layout = {
            'title': '分数分布雷达图',
            'polar': {
                'radialaxis': {
                    'visible': True,
                    'range': [0, 100]
                }
            },
            'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
        }

        return json.dumps(chart_data)
