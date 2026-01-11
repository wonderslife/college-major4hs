"""
历史分析API Blueprint
提供历史数据分析接口
"""

from flask import Blueprint, request, jsonify
from utils.logger import get_logger

history_bp = Blueprint('history', __name__)
logger = get_logger("history_bp")


@history_bp.route('/api/history/schools')
def get_history_schools():
    """获取历史数据中的所有学校"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        # TODO: 从history_loader获取学校列表
        # if keyword:
        #     schools = history_loader.search_schools(keyword)
        # else:
        #     schools = history_loader.get_school_list()
        
        return jsonify([])
    except Exception as e:
        logger.error(f"获取学校列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/api/history/school/<school_code>')
def get_history_school(school_code):
    """获取指定学校的历史分析数据"""
    try:
        # TODO: 从history_loader获取学校数据
        # school_data = history_loader.get_school_data(school_code)
        # if not school_data:
        #     return jsonify({'error': '学校不存在'}), 404
        # trend = history_loader.get_school_trend(school_code)
        
        return jsonify({})
    except Exception as e:
        logger.error(f"获取学校历史数据失败: {e}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/api/history/majors')
def get_history_majors():
    """获取所有专业列表或某个学校的专业列表"""
    try:
        keyword = request.args.get('keyword', '').strip()
        school_code = request.args.get('school_code', '').strip()
        
        # TODO: 从history_loader获取专业列表
        # if school_code:
        #     if keyword:
        #         majors = history_loader.search_school_majors(school_code, keyword)
        #     else:
        #         majors = history_loader.get_school_majors(school_code)
        # else:
        #     if keyword:
        #         majors = history_loader.search_majors(keyword)
        #     else:
        #         majors = history_loader.get_all_majors()
        
        return jsonify([])
    except Exception as e:
        logger.error(f"获取专业列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/api/history/major/<major_name>')
def get_history_major(major_name):
    """获取指定专业的历史数据"""
    try:
        # TODO: 从history_loader获取专业数据
        # major_data = history_loader.get_major_schools(major_name)
        # if not major_data:
        #     return jsonify({'error': '专业不存在'}), 404
        
        return jsonify({})
    except Exception as e:
        logger.error(f"获取专业历史数据失败: {e}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/api/history/compare')
def get_history_compare():
    """对比多所学校"""
    try:
        # 支持两种格式: codes=0247,0286 或 codes=0247&codes=0286
        codes_param = request.args.get('codes', '')
        
        if ',' in codes_param:
            # 逗号分隔格式
            school_codes = [c.strip() for c in codes_param.split(',') if c.strip()]
        else:
            # 重复参数格式
            school_codes = request.args.getlist('codes')
        
        if not school_codes or len(school_codes) > 10:
            return jsonify({'error': '请提供1-10个学校代码'}), 400
        
        # TODO: 从history_loader对比学校
        # comparison = history_loader.compare_schools(school_codes)
        
        return jsonify({})
    except Exception as e:
        logger.error(f"对比学校失败: {e}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/api/history/trend')
def get_history_trend():
    """获取趋势排行数据"""
    try:
        trend_type = request.args.get('type', 'score')  # score 或 rank
        direction = request.args.get('direction', 'desc')  # desc 或 asc
        limit = request.args.get('limit', 20, type=int)
        
        # 获取筛选条件
        is_985 = request.args.get('is_985', 'False').lower() == 'true'
        is_211 = request.args.get('is_211', 'False').lower() == 'true'
        is_double_first_class = request.args.get('is_double_first_class', 'False').lower() == 'true'
        
        # TODO: 从history_loader获取趋势数据
        # trend_data = []
        # for school in schools:
        #     trend = history_loader.get_school_trend(school['code'])
        #     if trend and len(trend.score_trend) == 3:
        #         tags = tag_manager.get_tags(school['name'])
        #         # 应用筛选条件并添加到trend_data
        
        return jsonify([])
    except Exception as e:
        logger.error(f"获取趋势排行失败: {e}")
        return jsonify({'error': str(e)}), 500
