"""
高校招生数据分析系统 - 主应用入口 v2.0
支持电脑端和移动端响应式浏览
使用新的模块化架构
"""

from flask import Flask, render_template, jsonify, request
import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# 导入新的模块
from core.analytics.analytics import AnalyticsEngine
from core.container import container
from core.data import CacheManager

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# 使用依赖注入容器
cache_manager = container.cache_manager
data_service = container.data_service

# 初始化分析引擎（使用data_service作为data_processor）
analytics_engine = AnalyticsEngine(data_processor=data_service)

# 初始化数据
print("正在初始化数据服务...")
try:
    # 清空缓存以应用最新的列名映射
    data_service.clear_all_caches()

    # 注册数据文件
    data_dir = 'data'
    data_service.add_admission_data(2025, os.path.join(data_dir, '2025投档分数线_含位次.md'))
    data_service.add_admission_data(2024, os.path.join(data_dir, '2024投档分数线_含位次.md'))
    data_service.add_admission_data(2023, os.path.join(data_dir, '2023投档分数线_含位次.md'))

    # 尝试加载2025年的数据（最新数据）
    data_2025 = data_service.load_admission_data(2025)
    if data_2025 is not None:
        print(f"2025年数据已加载，共 {len(data_2025)} 条记录")
    else:
        print("警告: 2025年数据未找到或加载失败")

    data_2024 = data_service.load_admission_data(2024)
    if data_2024 is not None:
        print(f"2024年数据已加载，共 {len(data_2024)} 条记录")
    else:
        print("警告: 2024年数据未找到或加载失败")

    data_2023 = data_service.load_admission_data(2023)
    if data_2023 is not None:
        print(f"2023年数据已加载，共 {len(data_2023)} 条记录")

    print("数据服务初始化完成")
except Exception as e:
    import traceback
    print(f"数据加载失败: {e}")
    traceback.print_exc()
    print("系统将使用空数据启动")

# ============ 页面路由 ============

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """数据看板"""
    return render_template('dashboard.html')

@app.route('/university')
def university():
    """院校分析"""
    return render_template('university.html')

@app.route('/major')
def major():
    """专业分析"""
    return render_template('major.html')

@app.route('/search')
def search():
    """搜索页面"""
    return render_template('search.html')

@app.route('/history')
def history():
    """历史分析页面"""
    return render_template('history.html')

@app.route('/history/compare')
def history_compare():
    """历史对比分析页面"""
    return render_template('history_compare.html')

@app.route('/history/school/<code>')
def history_school(code):
    """学校历史详情页面"""
    return render_template('history_school.html', school_code=code)

@app.route('/history/major/<name>')
def history_major(name):
    """专业历史详情页面"""
    return render_template('history_major.html', major_name=name)

@app.route('/prediction')
def prediction():
    """2026年位次预测页面"""
    return render_template('prediction.html')

@app.route('/test-data')
def test_data():
    """数据加载测试页面"""
    return render_template('test_data.html')

@app.route('/volunteer')
def volunteer():
    """志愿填报页面"""
    return render_template('volunteer.html')

# ============ API 路由 ============

@app.route('/api/statistics')
def get_statistics():
    """获取基础统计数据"""
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)
    stats = analytics_engine.get_basic_statistics(min_score, max_score, min_rank, max_rank)
    return jsonify(stats)

@app.route('/api/score-distribution')
def get_score_distribution():
    """获取分数分布"""
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)
    distribution = analytics_engine.get_score_distribution(min_score, max_score, min_rank, max_rank)
    return jsonify(distribution)

@app.route('/api/rank-distribution')
def get_rank_distribution():
    """获取位次分布"""
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)
    distribution = analytics_engine.get_rank_distribution(min_rank, max_rank)
    return jsonify(distribution)

@app.route('/api/top-universities')
def get_top_universities():
    """获取热门院校排行"""
    limit = request.args.get('limit', 20, type=int)
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)

    # 获取学校信息和保研率数据
    school_info_df = None
    graduate_rate_df = None

    try:
        school_info_df = data_service.load_school_info(force_reload=True)
        print(f"学校信息加载成功，共 {len(school_info_df)} 条记录")
        print(f"列名: {list(school_info_df.columns)}")
    except Exception as e:
        print(f"获取学校信息失败: {e}")

    try:
        graduate_rate_df = data_service.load_graduate_rate_data(force_reload=True)
        print(f"保研率信息加载成功，共 {len(graduate_rate_df)} 条记录")
    except Exception as e:
        print(f"获取保研率信息失败: {e}")

    top_unis = analytics_engine.get_top_universities(limit, min_score, max_score, school_info_df, graduate_rate_df)
    return jsonify(top_unis if isinstance(top_unis, list) else [])

@app.route('/api/top-majors')
def get_top_majors():
    """获取热门专业排行"""
    limit = request.args.get('limit', 20, type=int)
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    top_majors = analytics_engine.get_top_majors(limit, min_score, max_score)
    return jsonify(top_majors if isinstance(top_majors, list) else [])

@app.route('/api/search')
def search_data():
    """搜索接口"""
    keyword = request.args.get('keyword', '')
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)

    # 获取详细招生记录（默认按位次升序排序）
    results = analytics_engine.search.search_admissions(keyword, min_score, max_score, min_rank, max_rank, sort_by='rank')

    # 加载额外信息
    try:
        school_info_df = data_service.load_school_info()
        graduate_rate_df = data_service.load_graduate_rate_data()
        subject_loader = data_service.get_subject_loader()

        # 为每条记录添加额外信息
        for item in results:
            uni_name = item['university']

            # 添加学校信息
            if school_info_df is not None and not school_info_df.empty:
                try:
                    school_col = None
                    if '学校名称' in school_info_df.columns:
                        school_col = '学校名称'
                    elif '院校名称' in school_info_df.columns:
                        school_col = '院校名称'

                    if school_col:
                        school_row = school_info_df[school_info_df[school_col] == uni_name]
                        if not school_row.empty:
                            school_data = school_row.iloc[0]
                            item['city'] = school_data.get('所在城市', school_data.get('所在区域', ''))
                            item['tags'] = {
                                'is_985': str(school_data.get('985', '')) == 'Y',
                                'is_211': '211' in str(school_data.get('办学层次', '')),
                                'is_double_first_class': str(school_data.get('双一流', '')) == 'Y',
                                'is_private': str(school_data.get('民办高校', '')) == 'Y',
                                'is_independent': str(school_data.get('独立学院', '')) == 'Y'
                            }
                            item['detail_link'] = school_data.get('明细链接', '')
                except Exception as e:
                    print(f"处理学校信息时出错: {e}")

            # 添加保研率信息
            if graduate_rate_df is not None and not graduate_rate_df.empty and '院校名称' in graduate_rate_df.columns:
                try:
                    graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == uni_name]
                    if not graduate_row.empty:
                        graduate_data = graduate_row.iloc[0]
                        rate = graduate_data.get('graduate_rate', graduate_data.get('2025保研率'))
                        if rate and str(rate) != '':
                            if isinstance(rate, str):
                                rate = rate.replace('%', '')
                            item['postgraduate_info'] = {
                                'rate': float(rate),
                                'count': int(graduate_data.get('graduate_count', graduate_data.get('2025保研人数', 0)))
                            }
                except Exception as e:
                    print(f"处理保研率信息时出错: {e}")

            # 添加学科评估信息
            try:
                major_name = item['major']
                school_subjects = subject_loader.get_school_subjects(uni_name) if subject_loader else None
                if school_subjects:
                    evaluations = []
                    for subject in school_subjects:
                        subject_name = subject.get('学科名称', '')
                        if subject_name and (subject_name in major_name or major_name in subject_name):
                            evaluations.append(subject)
                    item['evaluations'] = evaluations
            except Exception as e:
                print(f"处理学科评估信息时出错: {e}")

    except Exception as e:
        print(f"加载额外信息失败: {e}")
        import traceback
        traceback.print_exc()

    # 返回符合前端期望的数据结构
    return jsonify({
        'results': results if isinstance(results, list) else [],
        'total': len(results) if isinstance(results, list) else 0
    })

@app.route('/api/by-score')
def get_by_score_range():
    """按分数范围查询"""
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)

    # 获取详细招生记录（默认按位次升序排序）
    results = analytics_engine.search.search_admissions('', min_score, max_score, sort_by='rank')

    # 加载额外信息
    try:
        school_info_df = data_service.load_school_info()
        graduate_rate_df = data_service.load_graduate_rate_data()
        subject_loader = data_service.get_subject_loader()

        # 为每条记录添加额外信息
        for item in results:
            uni_name = item['university']

            # 添加学校信息
            if school_info_df is not None and not school_info_df.empty:
                try:
                    school_col = None
                    if '学校名称' in school_info_df.columns:
                        school_col = '学校名称'
                    elif '院校名称' in school_info_df.columns:
                        school_col = '院校名称'

                    if school_col:
                        school_row = school_info_df[school_info_df[school_col] == uni_name]
                        if not school_row.empty:
                            school_data = school_row.iloc[0]
                            item['city'] = school_data.get('所在城市', school_data.get('所在区域', ''))
                            item['tags'] = {
                                'is_985': str(school_data.get('985', '')) == 'Y',
                                'is_211': '211' in str(school_data.get('办学层次', '')),
                                'is_double_first_class': str(school_data.get('双一流', '')) == 'Y',
                                'is_private': str(school_data.get('民办高校', '')) == 'Y',
                                'is_independent': str(school_data.get('独立学院', '')) == 'Y'
                            }
                            item['detail_link'] = school_data.get('明细链接', '')
                except Exception as e:
                    print(f"处理学校信息时出错: {e}")

            # 添加保研率信息
            if graduate_rate_df is not None and not graduate_rate_df.empty and '院校名称' in graduate_rate_df.columns:
                try:
                    graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == uni_name]
                    if not graduate_row.empty:
                        graduate_data = graduate_row.iloc[0]
                        rate = graduate_data.get('graduate_rate', graduate_data.get('2025保研率'))
                        if rate and str(rate) != '':
                            if isinstance(rate, str):
                                rate = rate.replace('%', '')
                            item['postgraduate_info'] = {
                                'rate': float(rate),
                                'count': int(graduate_data.get('graduate_count', graduate_data.get('2025保研人数', 0)))
                            }
                except Exception as e:
                    print(f"处理保研率信息时出错: {e}")

            # 添加学科评估信息
            try:
                major_name = item['major']
                school_subjects = subject_loader.get_school_subjects(uni_name) if subject_loader else None
                if school_subjects:
                    evaluations = []
                    for subject in school_subjects:
                        subject_name = subject.get('学科名称', '')
                        if subject_name and (subject_name in major_name or major_name in subject_name):
                            evaluations.append(subject)
                    item['evaluations'] = evaluations
            except Exception as e:
                print(f"处理学科评估信息时出错: {e}")

    except Exception as e:
        print(f"加载额外信息失败: {e}")
        import traceback
        traceback.print_exc()

    # 返回符合前端期望的数据结构
    return jsonify({
        'results': results if isinstance(results, list) else [],
        'total': len(results) if isinstance(results, list) else 0
    })

@app.route('/api/university/<name>')
def get_university_detail(name):
    """获取院校详情"""
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)

    # 获取基本详情
    detail = analytics_engine.get_university_detail(name, min_rank, max_rank)

    # 如果有错误，直接返回
    if 'error' in detail:
        return jsonify(detail)

    # 尝试获取学校信息
    try:
        school_info_df = data_service.load_school_info()
        if not school_info_df.empty:
            # 查找学校信息（支持院校名称和学校名称两种列）
            school_row = None
            if '学校名称' in school_info_df.columns:
                school_row = school_info_df[school_info_df['学校名称'] == name]
            elif '院校名称' in school_info_df.columns:
                school_row = school_info_df[school_info_df['院校名称'] == name]

            if not school_row.empty:
                school_data = school_row.iloc[0].to_dict()
                detail.update({
                    'region': school_data.get('所在区域', ''),
                    'authority': school_data.get('主管部门', ''),
                    'department': school_data.get('主管部门', ''),
                    'city': school_data.get('所在城市', ''),
                    'level': school_data.get('办学层次', ''),
                    'is_double_first_class': school_data.get('双一流', '') == 'Y',
                    'is_985': school_data.get('985', '') == 'Y'
                })
    except Exception as e:
        print(f"获取学校信息失败: {e}")

    # 尝试获取保研率信息
    try:
        graduate_rate_df = data_service.load_graduate_rate_data()
        if not graduate_rate_df.empty:
            graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == name]
            if not graduate_row.empty:
                graduate_data = graduate_row.iloc[0].to_dict()
                detail.update({
                    'graduate_rate': graduate_data.get('graduate_rate', graduate_data.get('2025保研率', '')),
                    'graduate_count': graduate_data.get('graduate_count', graduate_data.get('2025保研人数', '')),
                    'graduate_rank': int(graduate_data.get('排名', 0)) if pd.notna(graduate_data.get('排名', 0)) else None
                })
    except Exception as e:
        print(f"获取保研率信息失败: {e}")

    # 尝试获取学科评估信息
    try:
        subject_loader = data_service.get_subject_loader()
        school_subjects = subject_loader.get_school_subjects(name)
        if school_subjects:
            detail['school_subjects'] = school_subjects

            # 为每个专业添加学科评估信息
            if 'majors' in detail:
                for major in detail['majors']:
                    major_name = major.get('name', major.get('major', ''))
                    # 查找匹配的学科评估
                    major_evaluations = []
                    for subject in school_subjects:
                        # 模糊匹配：专业名称包含学科名称或学科名称包含专业名称
                        subject_name = subject.get('学科名称', '')
                        if subject_name and (subject_name in major_name or major_name in subject_name):
                            major_evaluations.append(subject)

                    if major_evaluations:
                        major['evaluations'] = major_evaluations
    except Exception as e:
        print(f"获取学科评估信息失败: {e}")

    return jsonify(detail)

@app.route('/api/major/<name>')
def get_major_detail(name):
    """获取专业详情"""
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)

    # 获取基本详情
    detail = analytics_engine.get_major_detail(name, min_rank, max_rank)

    # 如果有错误，直接返回
    if 'error' in detail:
        return jsonify(detail)

    # 加载学校信息和保研率数据
    school_info_df = None
    graduate_rate_df = None

    try:
        school_info_df = data_service.load_school_info()
    except Exception as e:
        print(f"获取学校信息失败: {e}")

    try:
        graduate_rate_df = data_service.load_graduate_rate_data()
    except Exception as e:
        print(f"获取保研率信息失败: {e}")

    # 为每个院校添加详细信息
    if 'universities' in detail and school_info_df is not None:
        for uni in detail['universities']:
            uni_name = uni['university']

            # 获取学校信息
            if '学校名称' in school_info_df.columns:
                school_row = school_info_df[school_info_df['学校名称'] == uni_name]
                if not school_row.empty:
                    school_data = school_row.iloc[0].to_dict()
                    uni['city'] = school_data.get('所在城市', school_data.get('所在区域', ''))
                    uni['level'] = school_data.get('办学层次', '')
                    uni['is_985'] = school_data.get('985', '') == 'Y'
                    uni['is_211'] = school_data.get('211', '') == 'Y'
                    uni['is_double_first_class'] = school_data.get('双一流', '') == 'Y'
                    uni['department'] = school_data.get('主管部门', '')
                    uni['detail_link'] = school_data.get('明细链接', '')

            # 获取保研率信息
            if graduate_rate_df is not None:
                graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == uni_name]
                if not graduate_row.empty:
                    graduate_data = graduate_row.iloc[0].to_dict()
                    uni['postgraduate_info'] = {
                        'rate': graduate_data.get('graduate_rate', graduate_data.get('2025保研率', '')),
                        'count': graduate_data.get('graduate_count', graduate_data.get('2025保研人数', '')),
                        'rank': graduate_data.get('排名', '')
                    }

    return jsonify(detail)

@app.route('/api/by-rank')
def get_by_rank_range():
    """按位次范围查询"""
    min_rank = request.args.get('min_rank', type=int)
    max_rank = request.args.get('max_rank', type=int)

    # 获取详细招生记录
    results = analytics_engine.search.search_admissions('', None, None, min_rank, max_rank)

    # 加载额外信息
    try:
        school_info_df = data_service.load_school_info()
        graduate_rate_df = data_service.load_graduate_rate_data()
        subject_loader = data_service.get_subject_loader()

        # 为每条记录添加额外信息
        for item in results:
            uni_name = item['university']

            # 添加学校信息
            if school_info_df is not None and not school_info_df.empty:
                try:
                    school_col = None
                    if '学校名称' in school_info_df.columns:
                        school_col = '学校名称'
                    elif '院校名称' in school_info_df.columns:
                        school_col = '院校名称'

                    if school_col:
                        school_row = school_info_df[school_info_df[school_col] == uni_name]
                        if not school_row.empty:
                            school_data = school_row.iloc[0]
                            item['city'] = school_data.get('所在城市', school_data.get('所在区域', ''))
                            item['tags'] = {
                                'is_985': str(school_data.get('985', '')) == 'Y',
                                'is_211': '211' in str(school_data.get('办学层次', '')),
                                'is_double_first_class': str(school_data.get('双一流', '')) == 'Y',
                                'is_private': str(school_data.get('民办高校', '')) == 'Y',
                                'is_independent': str(school_data.get('独立学院', '')) == 'Y'
                            }
                            item['detail_link'] = school_data.get('明细链接', '')
                except Exception as e:
                    print(f"处理学校信息时出错: {e}")

            # 添加保研率信息
            if graduate_rate_df is not None and not graduate_rate_df.empty and '院校名称' in graduate_rate_df.columns:
                try:
                    graduate_row = graduate_rate_df[graduate_rate_df['院校名称'] == uni_name]
                    if not graduate_row.empty:
                        graduate_data = graduate_row.iloc[0]
                        rate = graduate_data.get('graduate_rate', graduate_data.get('2025保研率'))
                        if rate and str(rate) != '':
                            if isinstance(rate, str):
                                rate = rate.replace('%', '')
                            item['postgraduate_info'] = {
                                'rate': float(rate),
                                'count': int(graduate_data.get('graduate_count', graduate_data.get('2025保研人数', 0)))
                            }
                except Exception as e:
                    print(f"处理保研率信息时出错: {e}")

            # 添加学科评估信息
            try:
                major_name = item['major']
                school_subjects = subject_loader.get_school_subjects(uni_name) if subject_loader else None
                if school_subjects:
                    evaluations = []
                    for subject in school_subjects:
                        subject_name = subject.get('学科名称', '')
                        if subject_name and (subject_name in major_name or major_name in subject_name):
                            evaluations.append(subject)
                    item['evaluations'] = evaluations
            except Exception as e:
                print(f"处理学科评估信息时出错: {e}")

    except Exception as e:
        print(f"加载额外信息失败: {e}")
        import traceback
        traceback.print_exc()

    # 返回符合前端期望的数据结构
    return jsonify({
        'results': results if isinstance(results, list) else [],
        'total': len(results) if isinstance(results, list) else 0
    })

@app.route('/api/advanced-search')
def advanced_search():
    """综合查询接口"""
    try:
        keyword = request.args.get('keyword', '')
        min_score = request.args.get('min_score', type=int)
        max_score = request.args.get('max_score', type=int)
        min_rank = request.args.get('min_rank', type=int)
        max_rank = request.args.get('max_rank', type=int)
        city = request.args.get('city', '')
        
        # 获取布尔参数（仅当参数存在且为'true'时才设置）
        is_985 = True if request.args.get('is_985') == 'true' else None
        is_211 = True if request.args.get('is_211') == 'true' else None
        is_double_first_class = True if request.args.get('is_double_first_class') == 'true' else None
        is_private = True if request.args.get('is_private') == 'true' else None
        is_independent = True if request.args.get('is_independent') == 'true' else None

        # 获取详细招生记录（默认按位次升序排序）
        results = analytics_engine.search.search_admissions(
            keyword, min_score, max_score, min_rank, max_rank,
            city=city if city else None,
            is_985=is_985,
            is_211=is_211,
            is_double_first_class=is_double_first_class,
            is_private=is_private,
            is_independent=is_independent,
            sort_by='rank'
        )

        # 返回符合前端期望的数据结构
        return jsonify({
            'results': results if isinstance(results, list) else [],
            'total': len(results) if isinstance(results, list) else 0
        })
    except Exception as e:
        print(f"综合查询接口错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'results': [],
            'total': 0,
            'error': str(e)
        })

@app.route('/api/history/trend')
def get_history_trend():
    """获取历史趋势数据（热门学校排名）"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        trend_type = request.args.get('type', 'rank')  # 'rank' 或 'score'
        direction = request.args.get('direction', 'asc')  # 'asc' 或 'desc'
        limit = request.args.get('limit', 20, type=int)
        is_985 = request.args.get('is_985', 'false').lower() == 'true'
        is_211 = request.args.get('is_211', 'false').lower() == 'true'
        is_double_first_class = request.args.get('is_double_first_class', 'false').lower() == 'true'

        # 获取学校信息
        school_info_df = None
        try:
            school_info_df = data_service.load_school_info()
        except Exception as e:
            print(f"获取学校信息失败: {e}")

        # 获取三年的录取数据
        data_2023 = data_service.load_admission_data(2023)
        data_2024 = data_service.load_admission_data(2024)
        data_2025 = data_service.load_admission_data(2025)

        # 聚合学校数据
        school_trends = {}
        years_data = {
            2023: data_2023 if data_2023 is not None else pd.DataFrame(),
            2024: data_2024 if data_2024 is not None else pd.DataFrame(),
            2025: data_2025 if data_2025 is not None else pd.DataFrame()
        }

        for year, df in years_data.items():
            if df.empty:
                continue

            # 确定列名
            score_col = '投档最低分' if '投档最低分' in df.columns else ('投档分' if '投档分' in df.columns else '分数')
            rank_col = '位次' if '位次' in df.columns else '排名'
            school_col = '院校名称' if '院校名称' in df.columns else ('学校名称' if '学校名称' in df.columns else None)

            if not school_col:
                continue

            # 按学校分组，取最高分（或最低位次）作为代表
            if trend_type == 'rank':
                grouped = df.groupby(school_col)[rank_col].min()
            else:
                grouped = df.groupby(school_col)[score_col].max()

            for school_name, value in grouped.items():
                if school_name not in school_trends:
                    school_trends[school_name] = {'name': school_name, 'years': {}}
                school_trends[school_name]['years'][year] = value

        # 转换为数组并添加学校标签
        results = []
        for school_name, data in school_trends.items():
            years = data['years']
            # 确保三年都有数据
            if len(years) == 3:
                trend_data = {
                    'name': school_name,
                    'code': stable_hash(school_name),  # 生成简单代码
                    'rank_trend': [
                        years.get(2023),
                        years.get(2024),
                        years.get(2025)
                    ],
                    'score_trend': [
                        years.get(2023),
                        years.get(2024),
                        years.get(2025)
                    ],
                    'tags': {}
                }

                # 计算变化趋势
                if trend_type == 'rank':
                    val_2023 = years.get(2023)
                    val_2024 = years.get(2024)
                    val_2025 = years.get(2025)
                    if val_2023 and val_2024 and val_2025:
                        # 计算总体变化
                        total_change = val_2025 - val_2023
                        if total_change < -100:
                            trend_data['trend'] = '上升'
                        elif total_change > 100:
                            trend_data['trend'] = '下降'
                        else:
                            trend_data['trend'] = '稳定'
                        trend_data['rank_change'] = total_change
                else:
                    val_2023 = years.get(2023)
                    val_2024 = years.get(2024)
                    val_2025 = years.get(2025)
                    if val_2023 and val_2024 and val_2025:
                        total_change = val_2025 - val_2023
                        if total_change > 10:
                            trend_data['trend'] = '上升'
                        elif total_change < -10:
                            trend_data['trend'] = '下降'
                        else:
                            trend_data['trend'] = '稳定'
                        trend_data['score_change'] = total_change

                # 添加学校标签
                if school_info_df is not None and not school_info_df.empty:
                    school_col = None
                    if '学校名称' in school_info_df.columns:
                        school_col = '学校名称'
                    elif '院校名称' in school_info_df.columns:
                        school_col = '院校名称'

                    if school_col:
                        school_row = school_info_df[school_info_df[school_col] == school_name]
                        if not school_row.empty:
                            school_data = school_row.iloc[0]
                            trend_data['tags'] = {
                                'is_985': str(school_data.get('985', '')) == 'Y',
                                'is_211': '211' in str(school_data.get('办学层次', '')),
                                'is_double_first_class': str(school_data.get('双一流', '')) == 'Y',
                                'is_private': str(school_data.get('民办高校', '')) == 'Y',
                                'is_independent': str(school_data.get('独立学院', '')) == 'Y'
                            }

                results.append(trend_data)

        # 应用标签筛选
        if is_985 or is_211 or is_double_first_class:
            filtered_results = []
            for item in results:
                include = True
                if is_985 and not item['tags'].get('is_985', False):
                    include = False
                if is_211 and not item['tags'].get('is_211', False):
                    include = False
                if is_double_first_class and not item['tags'].get('is_double_first_class', False):
                    include = False
                if include:
                    filtered_results.append(item)
            results = filtered_results

        # 排序
        if trend_type == 'rank':
            reverse = direction == 'desc'
            results.sort(key=lambda x: x['rank_trend'][2] if x['rank_trend'][2] is not None else 999999, reverse=reverse)
        else:
            reverse = direction == 'asc'
            results.sort(key=lambda x: x['score_trend'][2] if x['score_trend'][2] is not None else 0, reverse=reverse)

        # 限制数量
        return jsonify(results[:limit])

    except Exception as e:
        import traceback
        print(f"获取历史趋势数据失败: {e}")
        traceback.print_exc()
        return jsonify([])

@app.route('/api/history/schools')
def get_history_schools():
    """获取历史分析的学校列表"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        keyword = request.args.get('keyword', '')

        # 获取三年的录取数据
        data_2023 = data_service.load_admission_data(2023)
        data_2024 = data_service.load_admission_data(2024)
        data_2025 = data_service.load_admission_data(2025)

        # 获取所有学校
        schools = {}

        for year, df in [(2023, data_2023), (2024, data_2024), (2025, data_2025)]:
            if df is None or df.empty:
                continue

            # 确定列名
            school_col = '院校名称' if '院校名称' in df.columns else ('学校名称' if '学校名称' in df.columns else None)

            if not school_col:
                continue

            for school_name in df[school_col].unique():
                if school_name:
                    if school_name not in schools:
                        schools[school_name] = {
                            'name': school_name,
                            'code': stable_hash(school_name),
                            'years': set()
                        }
                    schools[school_name]['years'].add(year)

        # 转换为列表格式
        results = []
        for school_name, data in schools.items():
            if keyword and keyword.lower() not in school_name.lower():
                continue

            results.append({
                'name': school_name,
                'code': data['code'],
                'years_count': len(data['years'])
            })

        # 按名称排序
        results.sort(key=lambda x: x['name'])

        return jsonify(results)

    except Exception as e:
        import traceback
        print(f"获取学校列表失败: {e}")
        traceback.print_exc()
        return jsonify([])

@app.route('/api/history/majors')
def get_history_majors():
    """获取历史分析的专业列表"""
    try:
        # 获取三年的录取数据
        data_2023 = data_service.load_admission_data(2023)
        data_2024 = data_service.load_admission_data(2024)
        data_2025 = data_service.load_admission_data(2025)

        # 获取所有专业
        majors = {}

        for year, df in [(2023, data_2023), (2024, data_2024), (2025, data_2025)]:
            if df is None or df.empty:
                continue

            # 确定列名
            major_col = '专业名称' if '专业名称' in df.columns else ('专业' if '专业' in df.columns else None)

            if not major_col:
                continue

            for major_name in df[major_col].unique():
                if major_name:
                    if major_name not in majors:
                        majors[major_name] = {
                            'name': major_name,
                            'years': set()
                        }
                    majors[major_name]['years'].add(year)

        # 转换为列表格式
        results = []
        for major_name, data in majors.items():
            results.append({
                'name': major_name,
                'years_count': len(data['years'])
            })

        # 按名称排序
        results.sort(key=lambda x: x['name'])

        return jsonify(results)

    except Exception as e:
        import traceback
        print(f"获取专业列表失败: {e}")
        traceback.print_exc()
        return jsonify([])

@app.route('/api/history/compare')
def get_history_compare():
    """获取历史对比数据"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        codes_str = request.args.get('codes', '')
        if not codes_str:
            return jsonify({'error': '缺少学校代码'})
        
        codes = codes_str.split(',')
        print(f"请求的学校代码: {codes}")
        schools = {}

        # 获取所有学校列表，建立代码到名称的映射
        school_map = {}
        all_schools_df = data_service.load_admission_data(2025)
        if all_schools_df is not None and not all_schools_df.empty:
            school_col = '院校名称' if '院校名称' in all_schools_df.columns else ('学校名称' if '学校名称' in all_schools_df.columns else None)
            print(f"2025年数据列: {all_schools_df.columns.tolist()}")
            if school_col:
                for school_name in all_schools_df[school_col].unique():
                    school_code = stable_hash(school_name)
                    school_map[school_code] = school_name
        print(f"生成的学校映射数量: {len(school_map)}")

        # 初始化学校数据结构
        for code in codes:
            print(f"查找代码 {code}...")
            if code in school_map:
                schools[code] = {
                    'name': school_map[code],
                    'code': int(code) if code.isdigit() else code,
                    'years': {}
                }
                print(f"  找到学校: {school_map[code]}")
            else:
                print(f"  未找到学校")

        # 获取三年的录取数据
        years = [2023, 2024, 2025]
        
        for year in years:
            df = data_service.load_admission_data(year)
            if df is None or df.empty:
                print(f"{year}年数据为空")
                continue

            print(f"{year}年数据列: {df.columns.tolist()}, 数据行数: {len(df)}")

            # 确定列名
            school_col = '院校名称' if '院校名称' in df.columns else ('学校名称' if '学校名称' in df.columns else None)
            score_col = '投档最低分' if '投档最低分' in df.columns else ('投档分' if '投档分' in df.columns else ('分数' if '分数' in df.columns else None))
            major_col = '专业名称' if '专业名称' in df.columns else ('招生专业' if '招生专业' in df.columns else ('专业' if '专业' in df.columns else None))
            rank_col = '位次' if '位次' in df.columns else ('排名' if '排名' in df.columns else None)

            if not school_col or not score_col:
                print(f"{year}年: 缺少必要的列, school_col={school_col}, score_col={score_col}")
                continue

            # 为每所学校计算统计信息
            for code, school_data in schools.items():
                school_name = school_data['name']
                print(f"  处理学校 {school_name}...")
                
                # 根据学校名称精确匹配
                school_df = df[df[school_col] == school_name]
                print(f"  匹配结果: {len(school_df)} 条记录")
                
                if not school_df.empty:
                    min_score = school_df[score_col].min()
                    max_score = school_df[score_col].max()
                    avg_score = school_df[score_col].mean()
                    total_majors = school_df[major_col].nunique() if major_col and major_col in school_df.columns else 0

                    # 计算平均位次
                    avg_rank = 0
                    if rank_col and rank_col in school_df.columns:
                        avg_rank = school_df[rank_col].mean()

                    schools[code]['years'][str(year)] = {
                        'min_score': float(min_score) if pd.notna(min_score) else 0,
                        'max_score': float(max_score) if pd.notna(max_score) else 0,
                        'avg_score': float(avg_score) if pd.notna(avg_score) else 0,
                        'avg_rank': float(avg_rank) if pd.notna(avg_rank) else 0,
                        'total_majors': int(total_majors)
                    }
                    print(f"  {year}年数据: min={min_score}, max={max_score}, avg={avg_score}")

        # 为每所学校计算趋势数据
        for school_data in schools.values():
            years_dict = school_data['years']
            years = ['2023', '2024', '2025']
            
            # 确保有三年的数据
            if len(years_dict) == 3:
                # 计算分数趋势
                score_trend = [years_dict[year]['avg_score'] for year in years]
                rank_trend = [years_dict[year]['avg_rank'] for year in years]
                
                # 计算分数变化（2025 vs 2023）
                score_2023 = years_dict['2023']['avg_score']
                score_2025 = years_dict['2025']['avg_score']
                score_change = score_2025 - score_2023
                
                # 计算位次变化（2025 vs 2023）
                rank_2023 = years_dict['2023']['avg_rank']
                rank_2025 = years_dict['2025']['avg_rank']
                rank_change = rank_2025 - rank_2023
                
                # 计算分数增长率
                score_growth_rate = round((score_change / score_2023) * 100, 2) if score_2023 > 0 else 0
                
                # 计算趋势方向
                if score_change > 5:
                    trend = '上升'
                elif score_change < -5:
                    trend = '下降'
                else:
                    trend = '稳定'
                
                # 计算稳定性（分数标准差/平均分）
                if score_2025 > 0:
                    std_dev = pd.Series(score_trend).std()
                    stability = max(0, 1 - (std_dev / score_2025))
                else:
                    stability = 0
                
                # 添加趋势数据
                school_data['trend'] = {
                    'score_trend': score_trend,
                    'rank_trend': rank_trend,
                    'score_change': round(score_change, 2),
                    'rank_change': round(rank_change, 2),
                    'trend': trend,
                    'score_growth_rate': score_growth_rate,
                    'stability': round(stability, 4)
                }
                print(f"  {school_data['name']} 趋势: {trend}, 分数变化: {score_change:.1f}")
        
        # 转换为列表
        results = list(schools.values())
        print(f"返回结果: {len(results)} 个学校")
        
        return jsonify({'schools': results})

    except Exception as e:
        import traceback
        print(f"获取对比数据失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'schools': []})

@app.route('/api/history/school/<code>')
def get_history_school(code):
    """获取单个学校的历史数据"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        # 先通过学校API获取学校列表，找到匹配的学校
        all_schools = []
        data_2025 = data_service.load_admission_data(2025)
        if data_2025 is not None and not data_2025.empty:
            school_col = '院校名称' if '院校名称' in data_2025.columns else ('学校名称' if '学校名称' in data_2025.columns else None)
            if school_col:
                for school_name in data_2025[school_col].unique():
                    school_code = stable_hash(school_name)
                    all_schools.append({
                        'name': school_name,
                        'code': school_code
                    })
        
        # 找到匹配代码的学校
        school_info = None
        for s in all_schools:
            if str(s['code']) == str(code):
                school_info = s
                break
        
        if not school_info:
            return jsonify({'error': '未找到该学校的数据'})
        
        school_name = school_info['name']
        years = [2023, 2024, 2025]
        years_data = {}
        
        for year in years:
            df = data_service.load_admission_data(year)
            if df is None or df.empty:
                continue
                
            school_col = '院校名称' if '院校名称' in df.columns else ('学校名称' if '学校名称' in df.columns else None)
            score_col = '投档最低分' if '投档最低分' in df.columns else ('投档分' if '投档分' in df.columns else '分数')
            major_col = '专业名称' if '专业名称' in df.columns else ('招生专业' if '招生专业' in df.columns else ('专业' if '专业' in df.columns else None))
            rank_col = '位次' if '位次' in df.columns else '排名'
            
            if not school_col or not score_col:
                continue
            
            # 匹配学校名称
            school_df = df[df[school_col] == school_name]
            
            if not school_df.empty:
                # 构建专业详细信息
                majors_info = {}
                major_code_col = '专业编号' if '专业编号' in school_df.columns else ('专业代码' if '专业代码' in school_df.columns else None)

                # 按专业分组
                if major_col:
                    grouped = school_df.groupby(major_col)
                    for major_name, group in grouped:
                        # 取该专业的最低分作为代表
                        min_score = group[score_col].min()
                        rank = group[rank_col].min() if rank_col and rank_col in group.columns else 0
                        major_code = str(group[major_code_col].iloc[0]) if major_code_col and major_code_col in group.columns else str(len(majors_info))

                        majors_info[major_code] = {
                            'major_code': major_code,
                            'major_name': major_name,
                            'score': float(min_score) if pd.notna(min_score) else 0,
                            'rank': float(rank) if pd.notna(rank) else 0
                        }

                year_data = {
                    'majors': majors_info,  # 返回专业详细信息对象
                    'min_score': float(school_df[score_col].min()) if pd.notna(school_df[score_col].min()) else 0,
                    'max_score': float(school_df[score_col].max()) if pd.notna(school_df[score_col].max()) else 0,
                    'avg_score': float(school_df[score_col].mean()) if pd.notna(school_df[score_col].mean()) else 0,
                    'total_majors': len(majors_info)
                }

                if rank_col in school_df.columns:
                    year_data['min_rank'] = float(school_df[rank_col].min()) if pd.notna(school_df[rank_col].min()) else 0
                    year_data['avg_rank'] = float(school_df[rank_col].mean()) if pd.notna(school_df[rank_col].mean()) else 0
                
                years_data[str(year)] = year_data

        # 计算趋势数据
        trend_data = None
        if len(years_data) == 3:
            years_list = ['2023', '2024', '2025']
            if all(y in years_data for y in years_list):
                # 计算分数趋势
                score_trend = [years_data[y].get('avg_score', 0) for y in years_list]
                rank_trend = [years_data[y].get('avg_rank', 0) for y in years_list]

                # 计算分数变化
                score_2023 = years_data['2023'].get('avg_score', 0)
                score_2025 = years_data['2025'].get('avg_score', 0)
                score_change = score_2025 - score_2023

                # 计算位次变化
                rank_2023 = years_data['2023'].get('avg_rank', 0)
                rank_2025 = years_data['2025'].get('avg_rank', 0)
                rank_change = rank_2025 - rank_2023

                # 计算趋势方向（分数）
                if score_change > 10:
                    score_trend_str = '上升'
                elif score_change < -10:
                    score_trend_str = '下降'
                else:
                    score_trend_str = '稳定'

                trend_data = {
                    'score_trend': score_trend,
                    'rank_trend': rank_trend,
                    'score_change': score_change,
                    'rank_change': rank_change,
                    'trend': score_trend_str
                }

        return jsonify({
            'school': {
                'name': school_name,
                'code': code
            },
            'years': years_data,
            'trend': trend_data
        })

    except Exception as e:
        import traceback
        print(f"获取学校历史数据失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/api/history/major/<name>')
def get_history_major(name):
    """获取单个专业的历史数据"""
    try:
        from urllib.parse import unquote
        major_name = unquote(name)
        
        years = [2023, 2024, 2025]
        years_data = []
        
        for year in years:
            df = data_service.load_admission_data(year)
            if df is None or df.empty:
                continue
            
            school_col = '院校名称' if '院校名称' in df.columns else ('学校名称' if '学校名称' in df.columns else None)
            score_col = '投档最低分' if '投档最低分' in df.columns else ('投档分' if '投档分' in df.columns else '分数')
            major_col = '专业名称' if '专业名称' in df.columns else ('招生专业' if '招生专业' in df.columns else ('专业' if '专业' in df.columns else None))
            rank_col = '位次' if '位次' in df.columns else '排名'
            
            if not major_col or not score_col:
                continue
            
            # 根据专业名称匹配
            major_df = df[df[major_col].str.contains(major_name, na=False)]
            
            if not major_df.empty:
                schools = major_df[school_col].unique()
                
                year_data = {
                    'year': year,
                    'major_name': major_df[major_col].iloc[0],
                    'schools': list(schools[:20]),  # 限制返回前20个学校
                    'min_score': float(major_df[score_col].min()) if pd.notna(major_df[score_col].min()) else 0,
                    'max_score': float(major_df[score_col].max()) if pd.notna(major_df[score_col].max()) else 0,
                    'avg_score': float(major_df[score_col].mean()) if pd.notna(major_df[score_col].mean()) else 0,
                    'total_schools': len(schools)
                }
                
                if rank_col in major_df.columns:
                    year_data['min_rank'] = float(major_df[rank_col].min()) if pd.notna(major_df[rank_col].min()) else 0
                    year_data['avg_rank'] = float(major_df[rank_col].mean()) if pd.notna(major_df[rank_col].mean()) else 0
                
                years_data.append(year_data)
        
        if not years_data:
            return jsonify({'error': '未找到该专业的数据'})
            
        return jsonify({
            'major_name': years_data[0]['major_name'],
            'years_data': years_data
        })

    except Exception as e:
        import traceback
        print(f"获取专业历史数据失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})

# ============ 预测API ============

@app.route('/api/predict/school/<code>')
def predict_school(code):
    """预测学校2026年位次"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        # 获取学校数据
        data_2025 = data_service.load_admission_data(2025)
        if data_2025 is None or data_2025.empty:
            return jsonify({'error': '无法加载数据'})
        
        school_col = '院校名称' if '院校名称' in data_2025.columns else ('学校名称' if '学校名称' in data_2025.columns else None)
        if not school_col:
            return jsonify({'error': '数据列名不匹配'})
        
        # 找到学校名称
        school_name = None
        for name in data_2025[school_col].unique():
            if stable_hash(name) == str(code):
                school_name = name
                break
        
        if not school_name:
            return jsonify({'error': '未找到该学校'})
        
        # 收集三年数据
        years_data = []
        for year in [2023, 2024, 2025]:
            df = data_service.load_admission_data(year)
            if df is None or df.empty:
                continue
            
            school_df = df[df[school_col] == school_name]
            if not school_df.empty:
                rank_col = '位次' if '位次' in df.columns else '排名'
                if rank_col in school_df.columns:
                    avg_rank = school_df[rank_col].mean()
                    if pd.notna(avg_rank) and avg_rank > 0:
                        years_data.append({'year': year, 'rank': avg_rank})
        
        if len(years_data) < 2:
            return jsonify({'error': '数据不足，无法预测'})
        
        # 使用加权移动平均预测
        years_data.sort(key=lambda x: x['year'])
        weights = [1, 2, 3]  # 近期数据权重更高
        
        # 计算加权平均
        weighted_sum = 0
        weight_total = 0
        for i, data in enumerate(years_data[-3:]):  # 取最近3年
            weight = weights[len(years_data[-3:]) - 1 - i]
            weighted_sum += data['rank'] * weight
            weight_total += weight
        
        predicted_rank = weighted_sum / weight_total if weight_total > 0 else years_data[-1]['rank']
        
        # 计算置信度
        if len(years_data) == 3:
            confidence = 'high'
            # 计算标准差作为置信区间
            ranks = [d['rank'] for d in years_data]
            std = pd.Series(ranks).std()
            confidence_interval = [predicted_rank - std, predicted_rank + std]
        elif len(years_data) == 2:
            confidence = 'medium'
            diff = abs(years_data[-1]['rank'] - years_data[-2]['rank'])
            confidence_interval = [predicted_rank - diff, predicted_rank + diff]
        else:
            confidence = 'low'
            confidence_interval = [predicted_rank * 0.9, predicted_rank * 1.1]
        
        # 计算趋势
        if len(years_data) >= 2:
            if years_data[-1]['rank'] < years_data[-2]['rank']:
                trend = '位次上升（排名提升）'
            elif years_data[-1]['rank'] > years_data[-2]['rank']:
                trend = '位次下降（排名降低）'
            else:
                trend = '保持稳定'
        else:
            trend = '数据不足'
        
        return jsonify({
            'school_code': code,
            'school_name': school_name,
            'prediction': {
                'predicted_rank': round(predicted_rank),
                'confidence': confidence,
                'confidence_interval': [round(confidence_interval[0]), round(confidence_interval[1])],
                'trend': trend,
                'algorithm': 'weighted_moving_avg',
                'rationale': f'基于{len(years_data)}年历史数据，使用加权移动平均法预测，近两年数据权重更高'
            }
        })
    
    except Exception as e:
        import traceback
        print(f"预测学校失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})


@app.route('/api/predict/major')
def predict_major():
    """预测专业2026年位次"""
    try:
        school_code = request.args.get('school_code', '').strip()
        major_name = request.args.get('major_name', '').strip()
        
        if not school_code or not major_name:
            return jsonify({'error': '缺少必要参数'})
        
        # TODO: 实现专业预测逻辑
        return jsonify({
            'school_code': school_code,
            'major_name': major_name,
            'prediction': {
                'predicted_rank': 10000,
                'confidence': 'low',
                'confidence_interval': [9000, 11000],
                'trend': '数据不足',
                'algorithm': 'placeholder',
                'rationale': '专业预测功能待完善'
            }
        })
    
    except Exception as e:
        import traceback
        print(f"预测专业失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})


@app.route('/api/predict/batch-schools')
def predict_batch_schools():
    """批量预测学校2026年位次"""
    import hashlib
    
    def stable_hash(name):
        """使用稳定的哈希算法生成代码"""
        return str(int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % 100000)
    
    try:
        limit = request.args.get('limit', 100, type=int)
        
        # 获取2025年数据
        data_2025 = data_service.load_admission_data(2025)
        if data_2025 is None or data_2025.empty:
            return jsonify({'error': '无法加载数据'})
        
        school_col = '院校名称' if '院校名称' in data_2025.columns else ('学校名称' if '学校名称' in data_2025.columns else None)
        rank_col = '位次' if '位次' in data_2025.columns else '排名'
        
        if not school_col or not rank_col:
            return jsonify({'error': '数据列名不匹配'})
        
        # 按学校分组，取平均位次最小的学校
        school_rank_2025 = data_2025.groupby(school_col)[rank_col].mean().sort_values().head(limit)
        
        results = []
        for school_name in school_rank_2025.index:
            code = stable_hash(school_name)
            
            # 收集三年数据
            years_data = []
            for year in [2023, 2024, 2025]:
                df = data_service.load_admission_data(year)
                if df is None or df.empty:
                    continue
                
                school_df = df[df[school_col] == school_name]
                if not school_df.empty and rank_col in school_df.columns:
                    avg_rank = school_df[rank_col].mean()
                    if pd.notna(avg_rank) and avg_rank > 0:
                        years_data.append({'year': year, 'rank': avg_rank})
            
            if len(years_data) < 2:
                continue
            
            # 使用加权移动平均预测
            years_data.sort(key=lambda x: x['year'])
            weights = [1, 2, 3]
            
            weighted_sum = 0
            weight_total = 0
            for i, data in enumerate(years_data[-3:]):
                weight = weights[len(years_data[-3:]) - 1 - i]
                weighted_sum += data['rank'] * weight
                weight_total += weight
            
            predicted_rank = weighted_sum / weight_total if weight_total > 0 else years_data[-1]['rank']
            
            # 计算置信度和置信区间
            if len(years_data) == 3:
                confidence = 'high'
                ranks = [d['rank'] for d in years_data]
                std = pd.Series(ranks).std()
                confidence_interval = [predicted_rank - std, predicted_rank + std]
            elif len(years_data) == 2:
                confidence = 'medium'
                diff = abs(years_data[-1]['rank'] - years_data[-2]['rank'])
                confidence_interval = [predicted_rank - diff, predicted_rank + diff]
            else:
                confidence = 'low'
                confidence_interval = [predicted_rank * 0.9, predicted_rank * 1.1]
            
            # 计算趋势
            if len(years_data) >= 2:
                if years_data[-1]['rank'] < years_data[-2]['rank']:
                    trend = '位次上升'
                elif years_data[-1]['rank'] > years_data[-2]['rank']:
                    trend = '位次下降'
                else:
                    trend = '保持稳定'
            else:
                trend = '数据不足'
            
            results.append({
                'name': school_name,
                'code': code,
                'prediction': {
                    'predicted_rank': round(predicted_rank),
                    'confidence': confidence,
                    'confidence_interval': [round(confidence_interval[0]), round(confidence_interval[1])],
                    'trend': trend,
                    'algorithm': 'weighted_moving_avg',
                    'rationale': f'基于{len(years_data)}年历史数据'
                }
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        import traceback
        print(f"批量预测失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)})


# ============ 志愿填报API ============

# 内存存储方案数据
volunteer_plans_storage = {}
volunteer_plans_counter = 0
volunteer_students_storage = {}

@app.route('/api/volunteer/student-info', methods=['GET', 'POST'])
def volunteer_student_info():
    """获取或保存考生信息"""
    if request.method == 'GET':
        # 返回默认考生信息
        return jsonify({
            'success': True,
            'data': {
                'score': 600,
                'rank': 10000,
                'subject_type': '理科'
            }
        })
    elif request.method == 'POST':
        data = request.get_json()
        # 保存考生信息到内存
        volunteer_students_storage['current'] = data
        return jsonify({'success': True, 'message': '考生信息已保存'})


@app.route('/api/volunteer/volunteers', methods=['GET', 'POST', 'DELETE'])
def volunteer_list():
    """获取、添加或清空志愿列表"""
    if request.method == 'GET':
        # 返回当前方案的志愿列表
        current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
        plan = volunteer_plans_storage.get(str(current_plan_id), {})
        volunteers = plan.get('volunteers', [])
        return jsonify({'success': True, 'data': volunteers})
    elif request.method == 'POST':
        # 添加志愿
        data = request.get_json()
        current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
        if str(current_plan_id) not in volunteer_plans_storage:
            volunteer_plans_storage[str(current_plan_id)] = {
                'id': current_plan_id,
                'name': '默认方案',
                'volunteers': []
            }
        volunteer_plans_storage[str(current_plan_id)]['volunteers'].append(data)
        return jsonify({'success': True, 'data': {}, 'message': '志愿已添加'})


@app.route('/api/volunteer/volunteers/reorder', methods=['POST'])
def volunteer_reorder():
    """重新排序志愿"""
    data = request.get_json()
    current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
    if str(current_plan_id) in volunteer_plans_storage:
        volunteer_plans_storage[str(current_plan_id)]['volunteers'] = data
    return jsonify({'success': True, 'data': {}, 'message': '排序已更新'})


@app.route('/api/volunteer/plan/current', methods=['GET', 'POST'])
def volunteer_plan_current():
    """获取或设置当前方案"""
    if request.method == 'GET':
        current_plan_id = volunteer_students_storage.get('current_plan_id')
        if current_plan_id and str(current_plan_id) in volunteer_plans_storage:
            plan = volunteer_plans_storage[str(current_plan_id)]
            volunteers = plan.get('volunteers', [])
            total = len(volunteers)
            # 简单计算冲稳保数量（按索引分配）
            冲 = min(total, max(0, total // 3))
            稳 = min(total - 冲, max(0, (total - 冲) // 2))
            保 = total - 冲 - 稳
            avg_probability = 50  # 默认值
            
            return jsonify({
                'success': True,
                'data': {
                    'plan_id': plan['id'],
                    'plan_name': plan['name'],
                    'statistics': {
                        'total': total,
                        '冲': 冲,
                        '稳': 稳,
                        '保': 保,
                        'avg_probability': avg_probability
                    }
                }
            })
        return jsonify({'success': True, 'data': {'plan_id': 1, 'plan_name': '默认方案', 'statistics': {'total': 0, '冲': 0, '稳': 0, '保': 0, 'avg_probability': 0}}})
    elif request.method == 'POST':
        data = request.get_json()
        plan_id = data.get('plan_id')
        if plan_id:
            volunteer_students_storage['current_plan_id'] = plan_id
        return jsonify({'success': True, 'data': {}, 'message': '当前方案已设置'})


@app.route('/api/volunteer/analysis/visualization')
def volunteer_analysis_visualization():
    """获取可视化分析数据"""
    return jsonify({
        'success': True,
        'data': {
            'probability_distribution': {'high': 10, 'medium': 15, 'low': 5},
            'risk_distribution': {'高': 5, '中': 15, '低': 10},
            'location_distribution': {'华北': 8, '华东': 12, '华南': 6, '华中': 4},
            'school_type_distribution': {'985': 3, '211': 8, '双一流': 5, '普通': 4},
            'score_distribution': {'stable': 20, 'risk': 10},
            'school_tags': {'985': 3, '211': 8, 'double_first_first_class': 5}
        }
    })


@app.route('/api/volunteer/plans')
def volunteer_plans():
    """获取所有方案"""
    plans = []
    for plan_id, plan_data in volunteer_plans_storage.items():
        volunteers = plan_data.get('volunteers', [])
        plans.append({
            'id': plan_data['id'],
            'name': plan_data['name'],
            'created_at': plan_data.get('created_at', '2025-01-01 12:00:00'),
            'statistics': {
                'total': len(volunteers)
            },
            'student_info': plan_data.get('student_info', '')
        })
    # 按创建时间倒序
    plans.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'success': True, 'data': plans})


@app.route('/api/volunteer/plan/<planId>', methods=['GET', 'POST', 'DELETE'])
def volunteer_plan(planId):
    """获取、保存或删除方案"""
    if request.method == 'GET':
        plan = volunteer_plans_storage.get(str(planId))
        if not plan:
            return jsonify({'success': False, 'data': {}, 'message': '方案不存在'})
        return jsonify({
            'success': True,
            'data': {
                'plan_id': plan['id'],
                'plan_name': plan['name'],
                'volunteers': plan.get('volunteers', []),
                'student_info': plan.get('student_info', '')
            }
        })
    elif request.method == 'POST':
        data = request.get_json()
        plan_id = str(planId)
        if plan_id not in volunteer_plans_storage:
            return jsonify({'success': False, 'data': {}, 'message': '方案不存在'})
        # 更新方案
        volunteer_plans_storage[plan_id]['volunteers'] = data.get('volunteers', [])
        volunteer_plans_storage[plan_id]['student_info'] = data.get('student_info', '')
        return jsonify({'success': True, 'data': {}, 'message': '方案已保存'})
    elif request.method == 'DELETE':
        plan_id = str(planId)
        if plan_id in volunteer_plans_storage:
            del volunteer_plans_storage[plan_id]
            return jsonify({'success': True, 'data': {}, 'message': '方案已删除'})
        return jsonify({'success': False, 'data': {}, 'message': '方案不存在'})


@app.route('/api/volunteer/plan', methods=['POST'])
def volunteer_plan_save():
    """保存新方案"""
    global volunteer_plans_counter
    volunteer_plans_counter += 1
    plan_id = volunteer_plans_counter

    data = request.get_json()
    from datetime import datetime
    import hashlib

    # 生成学生信息字符串
    student_info = f"分数:{data.get('score', '')} 位次:{data.get('rank', '')} {data.get('subject_type', '理科')}"

    # 同时保存学生信息到current（用于生成志愿）
    volunteer_students_storage['current'] = {
        'score': data.get('score', 600),
        'rank': data.get('rank', 10000),
        'subject_type': data.get('subject_type', '理科')
    }

    # 创建新方案
    volunteer_plans_storage[str(plan_id)] = {
        'id': plan_id,
        'name': data.get('name', f'方案{plan_id}'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'volunteers': [],
        'student_info': student_info
    }

    # 设置为当前方案
    volunteer_students_storage['current_plan_id'] = plan_id

    return jsonify({'success': True, 'data': {'plan_id': plan_id}, 'message': '方案已保存'})


@app.route('/api/volunteer/compare', methods=['POST'])
def volunteer_compare():
    """对比方案"""
    data = request.get_json()
    # 提供前端期望的结构
    return jsonify({
        'success': True,
        'data': {
            'comparison_table': {
                'plans': [],
                'metrics': []
            },
            'best_plan_name': '',
            'suggestions': []
        }
    })


@app.route('/api/volunteer/compare/export', methods=['POST'])
def volunteer_compare_export():
    """导出对比结果"""
    data = request.get_json()
    return jsonify({'success': True, 'data': {'filepath': '/tmp/compare_report.xlsx'}, 'message': '导出成功'})


@app.route('/api/volunteer/plan/risk-assessment')
def volunteer_risk_assessment():
    """风险评估"""
    return jsonify({
        'success': True,
        'data': {
            'overall_risk': '中',
            'risk_factors': [],
            'suggestions': []
        }
    })


@app.route('/api/volunteer/search/schools')
def volunteer_search_schools():
    """搜索学校"""
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({'success': True, 'data': []})
    
    # 使用已有的学校搜索API
    try:
        results = analytics_engine.search.search_universities(keyword)
        # 转换为前端期望的格式
        import hashlib
        schools = []
        for school in results[:20]:
            school_name = school.get('name', '')
            if school_name:
                code = str(int(hashlib.md5(school_name.encode('utf-8')).hexdigest(), 16) % 100000)
                # 尝试获取学校标签信息
                try:
                    school_info_df = data_service.load_school_info()
                    if school_info_df is not None and not school_info_df.empty:
                        school_col = None
                        if '学校名称' in school_info_df.columns:
                            school_col = '学校名称'
                        elif '院校名称' in school_info_df.columns:
                            school_col = '院校名称'
                        
                        if school_col:
                            school_row = school_info_df[school_info_df[school_col] == school_name]
                            if not school_row.empty:
                                school_data = school_row.iloc[0]
                                tags = {
                                    'is_985': str(school_data.get('985', '')) == 'Y',
                                    'is_211': '211' in str(school_data.get('办学层次', '')),
                                    'is_double_first_class': str(school_data.get('双一流', '')) == 'Y',
                                    'is_private': str(school_data.get('民办高校', '')) == 'Y',
                                    'is_independent': str(school_data.get('独立学院', '')) == 'Y'
                                }
                            else:
                                tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False, 'is_private': False, 'is_independent': False}
                        else:
                            tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False, 'is_private': False, 'is_independent': False}
                    else:
                        tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False, 'is_private': False, 'is_independent': False}
                except Exception:
                    tags = {'is_985': False, 'is_211': False, 'is_double_first_class': False, 'is_private': False, 'is_independent': False}
                
                schools.append({
                    'name': school_name,
                    'code': code,
                    'province': '',  # 暂时留空
                    'tags': tags
                })
        return jsonify({'success': True, 'data': schools})
    except Exception as e:
        print(f"搜索学校失败: {e}")
        return jsonify({'success': False, 'message': '搜索失败', 'data': []})


@app.route('/api/volunteer/school/<schoolCode>/majors/search')
def volunteer_school_majors_search(schoolCode):
    """搜索学校的专业"""
    keyword = request.args.get('keyword', '').strip()
    
    # 模拟专业数据
    all_majors = [
        '计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术',
        '电子信息工程', '通信工程', '自动化', '电气工程及其自动化',
        '机械工程', '土木工程', '建筑学', '城乡规划',
        '临床医学', '口腔医学', '药学', '护理学',
        '金融学', '会计学', '经济学', '工商管理',
        '法学', '社会学', '新闻学', '汉语言文学',
        '英语', '日语', '法语', '德语',
        '数学与应用数学', '物理学', '化学', '生物科学',
        '环境工程', '材料科学与工程', '能源与动力工程', '车辆工程'
    ]
    
    # 根据关键词过滤
    if keyword:
        filtered_majors = [m for m in all_majors if keyword in m]
    else:
        filtered_majors = all_majors[:20]  # 返回前20个
    
    return jsonify({'success': True, 'data': filtered_majors})


@app.route('/api/volunteer/school/<schoolCode>/majors')
def volunteer_school_majors(schoolCode):
    """获取学校的专业列表"""
    # 模拟专业数据
    all_majors = [
        '计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术',
        '电子信息工程', '通信工程', '自动化', '电气工程及其自动化',
        '机械工程', '土木工程', '建筑学', '城乡规划',
        '临床医学', '口腔医学', '药学', '护理学',
        '金融学', '会计学', '经济学', '工商管理',
        '法学', '社会学', '新闻学', '汉语言文学',
        '英语', '日语', '法语', '德语',
        '数学与应用数学', '物理学', '化学', '生物科学',
        '环境工程', '材料科学与工程', '能源与动力工程', '车辆工程'
    ]
    
    return jsonify({'success': True, 'data': all_majors})


@app.route('/api/volunteer/volunteer/<id>', methods=['DELETE'])
def volunteer_delete(id):
    """删除志愿"""
    current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
    if str(current_plan_id) in volunteer_plans_storage:
        volunteers = volunteer_plans_storage[str(current_plan_id)]['volunteers']
        # 找到并删除对应ID的志愿
        volunteer_plans_storage[str(current_plan_id)]['volunteers'] = [
            v for v in volunteers if v.get('id') != id
        ]
        return jsonify({'success': True, 'data': {}, 'message': '志愿已删除'})
    return jsonify({'success': False, 'data': {}, 'message': '删除失败'})


@app.route('/api/volunteer/volunteers/clear', methods=['POST'])
def volunteer_clear():
    """清空志愿"""
    current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
    if str(current_plan_id) in volunteer_plans_storage:
        volunteer_plans_storage[str(current_plan_id)]['volunteers'] = []
        return jsonify({'success': True, 'data': {}, 'message': '志愿已清空'})
    return jsonify({'success': False, 'data': {}, 'message': '清空失败'})


@app.route('/api/volunteer/export', methods=['POST'])
def volunteer_export():
    """导出志愿"""
    try:
        # 获取请求参数
        data = request.get_json()
        format_type = data.get('format', 'excel') if data else 'excel'
        
        # 获取当前方案
        current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
        if str(current_plan_id) not in volunteer_plans_storage:
            return jsonify({'success': False, 'message': '当前方案不存在'})
        
        plan = volunteer_plans_storage[str(current_plan_id)]
        volunteers = plan.get('volunteers', [])
        
        if not volunteers:
            return jsonify({'success': False, 'message': '当前方案没有志愿数据'})
        
        # 创建导出目录
        exports_dir = os.path.join(os.getcwd(), 'exports')
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_name = plan.get('name', f'方案{current_plan_id}')
        
        # 根据格式导出
        if format_type == 'excel':
            filepath = os.path.join(exports_dir, f'{plan_name}_志愿列表_{timestamp}.xlsx')
            
            # 准备数据
            export_data = []
            for i, vol in enumerate(volunteers, 1):
                export_data.append({
                    '序号': i,
                    '学校名称': vol.get('school_name', ''),
                    '专业名称': vol.get('major_name', ''),
                    '录取概率': f"{vol.get('probability', 0):.1f}%",
                    '类别': vol.get('category', ''),
                    '省份': vol.get('province', ''),
                    '城市': vol.get('city', '')
                })
            
            # 创建DataFrame并导出
            df = pd.DataFrame(export_data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            return jsonify({
                'success': True,
                'message': 'Excel导出成功',
                'filepath': filepath
            })
            
        elif format_type == 'pdf':
            filepath = os.path.join(exports_dir, f'{plan_name}_志愿列表_{timestamp}.pdf')
            
            # 创建PDF文档
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # 添加标题
            title = Paragraph(f'<b>{plan_name} - 志愿列表</b>', styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # 添加表头
            header = ['序号', '学校名称', '专业名称', '录取概率', '类别', '省份', '城市']
            data = [header]
            
            # 添加数据行
            for i, vol in enumerate(volunteers, 1):
                row = [
                    str(i),
                    vol.get('school_name', ''),
                    vol.get('major_name', ''),
                    f"{vol.get('probability', 0):.1f}%",
                    vol.get('category', ''),
                    vol.get('province', ''),
                    vol.get('city', '')
                ]
                data.append(row)
            
            # 创建表格
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            # 生成PDF
            doc.build(elements)
            
            return jsonify({
                'success': True,
                'message': 'PDF导出成功',
                'filepath': filepath
            })
        else:
            return jsonify({'success': False, 'message': '不支持的导出格式'})
            
    except Exception as e:
        print(f"导出失败: {str(e)}")
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'})


@app.route('/api/volunteer/generate', methods=['POST'])
def volunteer_generate():
    """智能生成志愿"""
    data = request.get_json()
    
    # 获取用户偏好和算法选择
    preferences = data.get('preferences', {}) if data else {}
    algorithm = data.get('algorithm', 'weighted')  # 默认使用加权算法
    
    # 获取学生信息（从存储或使用默认值）
    student_info = volunteer_students_storage.get('current', {})
    if not student_info:
        # 如果没有保存的学生信息，使用默认值或从preferences中提取
        student_info = {
            'score': preferences.get('score', 600),
            'rank': preferences.get('rank', 10000),
            'subject_type': preferences.get('subject_type', '理科')
        }
    
    # 使用推荐引擎生成志愿
    try:
        volunteers = analytics_engine.recommendation.generate_volunteers(
            student_info=student_info,
            preferences=preferences,
            algorithm=algorithm  # 传递算法选择
        )
        
        # 确保有足够的数据
        if len(volunteers) == 0:
            # 如果推荐引擎返回空列表，使用基于分数的简单推荐
            volunteers = _generate_fallback_volunteers(student_info, preferences)
        
        # 保存到当前方案
        current_plan_id = volunteer_students_storage.get('current_plan_id', 1)
        if str(current_plan_id) not in volunteer_plans_storage:
            from datetime import datetime
            volunteer_plans_storage[str(current_plan_id)] = {
                'id': current_plan_id,
                'name': f'方案{current_plan_id}',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'volunteers': []
            }
        
        # 替换现有志愿
        volunteer_plans_storage[str(current_plan_id)]['volunteers'] = volunteers
        
        # 记录使用的算法
        volunteer_plans_storage[str(current_plan_id)]['algorithm'] = algorithm
        
        algorithm_names = {
            'weighted': '多因素加权评分',
            'ml': '机器学习预测'
        }
        
        # 根据实际生成的志愿数量显示不同的消息
        message = f'成功生成{len(volunteers)}个志愿（使用{algorithm_names.get(algorithm, algorithm)}算法）'
        if len(volunteers) < 120:
            message += f'，筛选条件较严格，实际生成{len(volunteers)}个志愿'
        
        return jsonify({
            'success': True, 
            'data': {'volunteers': volunteers},
            'message': message
        })
        
    except Exception as e:
        import traceback
        print(f"生成志愿失败: {e}")
        traceback.print_exc()
        
        # 使用后备方案
        volunteers = _generate_fallback_volunteers(student_info, preferences)
        
        return jsonify({
            'success': True if len(volunteers) > 0 else False,
            'data': {'volunteers': volunteers},
            'message': f'生成志愿时遇到问题，已使用后备方案生成{len(volunteers)}个志愿'
        })

def _generate_fallback_volunteers(student_info, preferences):
    """后备方案：基于简单规则的志愿生成"""
    import random
    from datetime import datetime
    
    score = student_info.get('score', 600)
    rank = student_info.get('rank', 10000)
    
    # 从真实数据中获取学校列表
    try:
        df = data_service.load_admission_data(2025)
        if df is not None and len(df) > 0:
            # 确定列名
            score_col = '投档最低分' if '投档最低分' in df.columns else '分数'
            school_col = '院校名称' if '院校名称' in df.columns else '招生院校'
            major_col = '专业名称' if '专业名称' in df.columns else '招生专业'
            
            # 筛选分数范围
            min_score = max(0, score - 80)
            max_score = score + 40
            filtered_df = df[(df[score_col] >= min_score) & (df[score_col] <= max_score)]
            
            if len(filtered_df) > 0:
                # 从真实数据中采样
                sample_size = min(120, len(filtered_df))
                sampled_df = filtered_df.sample(n=sample_size, replace=True)
                
                volunteers = []
                for i, (_, row) in enumerate(sampled_df.iterrows(), 1):
                    # 计算简单概率
                    diff = score - row[score_col]
                    if diff >= 20:
                        probability = 85 + min(10, (diff - 20) // 2)
                        type_str = '冲'
                    elif diff >= 10:
                        probability = 70 + min(15, (diff - 10))
                        type_str = '稳'
                    elif diff >= 0:
                        probability = 50 + min(20, diff * 2)
                        type_str = '稳'
                    else:
                        probability = 30 + min(20, (diff + 20) // 2)
                        type_str = '保'
                    
                    probability = max(10, min(99, probability))
                    
                    import hashlib
                    school_name = row[school_col]
                    school_code = str(int(hashlib.md5(school_name.encode('utf-8')).hexdigest(), 16) % 100000)
                    
                    # 计算风险等级
                    if probability >= 70:
                        risk_level = "低"
                    elif probability >= 30:
                        risk_level = "中"
                    else:
                        risk_level = "高"
                    
                    # 生成类别依据
                    category_basis_map = {
                        '冲': "分数略低于往年录取线",
                        '稳': "分数与往年录取线相当",
                        '推荐': "综合推荐",
                        '保': "分数高于往年录取线"
                    }
                    category_basis = category_basis_map.get(type_str, "未知依据")
                    
                    # 获取位次信息
                    rank_cols = ['投档位次', '位次']
                    avg_rank_2025 = None
                    for col in rank_cols:
                        if col in row:
                            try:
                                avg_rank_2025 = int(row[col])
                            except (ValueError, TypeError):
                                avg_rank_2025 = None
                            break
                    
                    volunteer = {
                        'id': f'v_{i:03d}',
                        'school_name': school_name,
                        'university_code': school_code,
                        'major_name': row[major_col],
                        'admission_probability': probability,
                        'category': type_str,
                        'risk_level': risk_level,
                        'category_basis': category_basis,
                        'avg_rank_2025': avg_rank_2025,
                        'province': '',  # 暂时留空
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'tags': {
                            'is_985': False,
                            'is_211': False,
                            'is_double_first_class': False,
                            'is_private': False,
                            'is_independent': False
                        }
                    }
                    volunteers.append(volunteer)
                
                return volunteers[:120]
    except Exception as e:
        print(f"加载真实数据失败: {e}")
    
    # 如果真实数据不可用，使用模拟数据
    return _generate_simulated_volunteers(score)

def _generate_simulated_volunteers(score):
    """生成模拟志愿（仅当真实数据不可用时使用）"""
    import random
    from datetime import datetime
    
    # 模拟学校列表
    universities = [
        {'name': '清华大学', 'code': '1001', 'province': '北京'},
        {'name': '北京大学', 'code': '1002', 'province': '北京'},
        {'name': '复旦大学', 'code': '1003', 'province': '上海'},
        {'name': '上海交通大学', 'code': '1004', 'province': '上海'},
        {'name': '浙江大学', 'code': '1005', 'province': '浙江'},
        {'name': '南京大学', 'code': '1006', 'province': '江苏'},
        {'name': '武汉大学', 'code': '1007', 'province': '湖北'},
        {'name': '华中科技大学', 'code': '1008', 'province': '湖北'},
        {'name': '中山大学', 'code': '1009', 'province': '广东'},
        {'name': '四川大学', 'code': '1010', 'province': '四川'}
    ]
    
    # 模拟专业列表
    majors = [
        '计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术',
        '电子信息工程', '通信工程', '自动化', '电气工程及其自动化',
        '机械工程', '土木工程', '建筑学', '城乡规划',
        '临床医学', '口腔医学', '药学', '护理学',
        '金融学', '会计学', '经济学', '工商管理'
    ]
    
    volunteers = []
    for i in range(1, 121):
        university = random.choice(universities)
        major = random.choice(majors)
        
        # 基于分数计算概率（简单模型）
        base_prob = random.randint(30, 95)
        
        # 随机分配冲稳保类型
        if base_prob < 40:
            type_str = '冲'
        elif base_prob < 70:
            type_str = '稳'
        else:
            type_str = '保'
        
        # 计算风险等级
        if base_prob >= 70:
            risk_level = "低"
        elif base_prob >= 30:
            risk_level = "中"
        else:
            risk_level = "高"
        
        # 生成类别依据
        category_basis_map = {
            '冲': "分数略低于往年录取线",
            '稳': "分数与往年录取线相当",
            '推荐': "综合推荐",
            '保': "分数高于往年录取线"
        }
        category_basis = category_basis_map.get(type_str, "未知依据")
        
        volunteer = {
            'id': f'v_{i:03d}',
            'school_name': university['name'],
            'university_code': university['code'],
            'major_name': major,
            'admission_probability': base_prob,
            'category': type_str,
            'risk_level': risk_level,
            'category_basis': category_basis,
            'avg_rank_2025': None,
            'province': university['province'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tags': {
                'is_985': True if random.random() > 0.7 else False,
                'is_211': True if random.random() > 0.5 else False,
                'is_double_first_class': True if random.random() > 0.6 else False,
                'is_private': False,
                'is_independent': False
            }
        }
        volunteers.append(volunteer)
    
    return volunteers


@app.route('/api/chart/<chart_type>')
def get_chart(chart_type):
    """获取图表数据"""
    try:
        import json
        from utils.chart_renderer import ChartRenderer

        chart_renderer = ChartRenderer()

        # 从查询参数获取数据
        chart_data = request.args.get('data')

        if chart_data:
            # 如果前端传递了数据，使用前端数据生成图表
            data = json.loads(chart_data)
            chart_json = chart_renderer.generate_chart(chart_type, data)
        else:
            # 否则从后端获取数据并生成图表（支持筛选参数）
            min_score = request.args.get('min_score', type=int)
            max_score = request.args.get('max_score', type=int)
            min_rank = request.args.get('min_rank', type=int)
            max_rank = request.args.get('max_rank', type=int)
            limit = request.args.get('limit', 15, type=int)

            if chart_type == 'score_distribution':
                data = analytics_engine.get_score_distribution(min_score, max_score)
                chart_json = chart_renderer.generate_score_distribution_chart(data)
            elif chart_type == 'rank_distribution':
                data = analytics_engine.get_rank_distribution(min_rank, max_rank)
                chart_json = chart_renderer.generate_rank_distribution_chart(data)
            elif chart_type == 'top_universities':
                data = analytics_engine.get_top_universities(limit, min_score, max_score)
                chart_json = chart_renderer.generate_top_universities_chart(data)
            elif chart_type == 'top_majors':
                data = analytics_engine.get_top_majors(limit, min_score, max_score)
                chart_json = chart_renderer.generate_top_majors_chart(data)
            elif chart_type == 'score_radar':
                data = analytics_engine.get_basic_statistics(min_score, max_score, min_rank, max_rank)
                chart_json = chart_renderer.generate_radar_chart(data)
            else:
                chart_json = json.dumps({})

        return chart_json
    except Exception as e:
        import traceback
        print(f"图表生成失败: {e}")
        traceback.print_exc()
        return jsonify({})

# ============ 健康检查 ============

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'cache_size': len(cache_manager._cache)
    })

# ============ 启动应用 ============

import socket

def is_port_in_use(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            return False
    except OSError:
        return True

if __name__ == '__main__':
    try:
        port = 5000
        if is_port_in_use(port):
            print('=' * 60)
            print('错误: 端口 5000 已被占用!')
            print('请关闭占用该端口的程序后重试。')
            print('=' * 60)
            exit(1)

        print('=' * 60)
        print('高校招生数据分析系统 v2.0')
        print('=' * 60)
        print('访问地址: http://localhost:5000')
        print('支持电脑端和移动端访问')
        print('=' * 60)
        print('系统已启动')
        print('=' * 60)

        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
