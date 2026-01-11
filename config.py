"""
生产环境配置
"""
import os
from pathlib import Path


class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college-data-analysis-secret-key-2026')
    DEBUG = False
    TESTING = False

    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5000

    # 项目路径
    BASE_DIR = Path(__file__).parent

    # 数据目录
    DATA_DIR = BASE_DIR / 'data'
    CACHE_DIR = BASE_DIR / 'cache'
    EXPORT_DIR = BASE_DIR / 'exports'
    LOG_DIR = BASE_DIR / 'logs'

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10

    # 缓存配置
    CACHE_MAX_SIZE = 1000
    CACHE_TTL = 3600  # 1小时

    # 数据处理配置
    BATCH_SIZE = 1000
    MAX_WORKERS = 4

    # API配置
    API_PER_PAGE = 20
    API_MAX_PER_PAGE = 100

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'pdf'}

    # 性能配置
    ENABLE_CACHE = True
    ENABLE_LOGGING = True


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    HOST = '127.0.0.1'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    HOST = '0.0.0.0'

    # 生产环境特定配置
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)

    # 性能优化
    CACHE_MAX_SIZE = 2000
    CACHE_TTL = 7200  # 2小时

    # 日志优化
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    # 测试特定配置
    CACHE_DIR = BASE_DIR / 'cache' / 'test'
    LOG_DIR = BASE_DIR / 'logs' / 'test'


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """获取配置"""
    if env is None:
        env = os.environ.get('FLASK_ENV', os.environ.get('ENV', 'development'))
    return config.get(env, config['default'])
