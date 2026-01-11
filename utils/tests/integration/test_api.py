"""
API集成测试
"""
import pytest
import json
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client():
    """创建Flask测试客户端"""
    from app import app
    app.config['TESTING'] = True
    return app.test_client()


class TestDataAPI:
    """测试数据查询API"""
    
    def test_statistics_api(self, client):
        """测试统计API"""
        response = client.get('/api/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_records" in data
        assert "score_range" in data
        assert "rank_range" in data
    
    def test_score_distribution_api(self, client):
        """测试分数分布API"""
        response = client.get('/api/score-distribution')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "bins" in data
        assert "counts" in data
    
    def test_rank_distribution_api(self, client):
        """测试位次分布API"""
        response = client.get('/api/rank-distribution')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "bins" in data
        assert "counts" in data
    
    def test_top_universities_api(self, client):
        """测试热门院校API"""
        response = client.get('/api/top-universities?limit=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_top_majors_api(self, client):
        """测试热门专业API"""
        response = client.get('/api/top-majors?limit=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_search_api(self, client):
        """测试搜索API"""
        response = client.get('/api/search?keyword=北京大学&page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "results" in data
        assert "pagination" in data
    
    def test_by_score_api(self, client):
        """测试按分数查询API"""
        response = client.get('/api/by-score?min_score=600&max_score=700')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_by_rank_api(self, client):
        """测试按位次查询API"""
        response = client.get('/api/by-rank?min_rank=1000&max_rank=5000')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_university_detail_api(self, client):
        """测试院校详情API"""
        # 假设北京大学存在
        response = client.get('/api/university/北京大学')
        
        assert response.status_code in [200, 404]  # 可能不存在，返回404
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "school_name" in data
    
    def test_major_detail_api(self, client):
        """测试专业详情API"""
        response = client.get('/api/major/经济学')
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "major_name" in data


class TestHistoryAPI:
    """测试历史分析API"""
    
    def test_history_schools_api(self, client):
        """测试历史学校列表API"""
        response = client.get('/api/history/schools')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_school_history_api(self, client):
        """测试学校历史数据API"""
        response = client.get('/api/history/school/10001')
        
        assert response.status_code in [200, 404]
    
    def test_history_compare_api(self, client):
        """测试历史对比API"""
        response = client.get('/api/history/compare?schools=10001,10002')
        
        assert response.status_code in [200, 400]
    
    def test_history_trend_api(self, client):
        """测试历史趋势API"""
        response = client.get('/api/history/trend?field=score_2025&limit=10')
        
        assert response.status_code in [200, 400]


class TestPredictionAPI:
    """测试预测API"""
    
    def test_predict_school_api(self, client):
        """测试学校预测API"""
        response = client.get('/api/predict/school/10001')
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "school_name" in data
            assert "predictions" in data
    
    def test_predict_major_api(self, client):
        """测试专业预测API"""
        response = client.get('/api/predict/major?major_name=经济学&user_rank=1000')
        
        assert response.status_code in [200, 400]
    
    def test_batch_predict_schools_api(self, client):
        """测试批量预测API"""
        response = client.post(
            '/api/predict/batch-schools',
            json={"school_codes": ["10001", "10002"], "user_rank": 1000}
        )
        
        assert response.status_code in [200, 400]


class TestExportAPI:
    """测试导出API"""
    
    def test_export_excel_api(self, client):
        """测试Excel导出API"""
        response = client.get('/api/export/excel?keyword=北京大学')
        
        assert response.status_code in [200, 400]
    
    def test_export_csv_api(self, client):
        """测试CSV导出API"""
        response = client.get('/api/export/csv?keyword=北京大学')
        
        assert response.status_code in [200, 400]
    
    def test_export_pdf_api(self, client):
        """测试PDF导出API"""
        response = client.get('/api/export/pdf?keyword=北京大学')
        
        assert response.status_code in [200, 400]


class TestPageAPIs:
    """测试页面API"""
    
    def test_index_page(self, client):
        """测试首页"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'高校招生数据分析系统' in response.data
    
    def test_dashboard_page(self, client):
        """测试数据看板页面"""
        response = client.get('/dashboard')
        
        assert response.status_code == 200
    
    def test_university_page(self, client):
        """测试院校分析页面"""
        response = client.get('/university')
        
        assert response.status_code == 200
    
    def test_major_page(self, client):
        """测试专业分析页面"""
        response = client.get('/major')
        
        assert response.status_code == 200
    
    def test_search_page(self, client):
        """测试搜索页面"""
        response = client.get('/search')
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
