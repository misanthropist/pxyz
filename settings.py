import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'kjdflsdjf')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    PXYZ_ITEM_PER_PAGE = 12
    PXYZ_USER_PER_PAGE = 12

    PXYZ_MAX_FILE_SIZE = 1024*1024*10
    PXYZ_MAX_COVER_SIZE = 1024*100
    PXYZ_UPLOAD_PATH = os.path.join(basedir, 'pxyz', 'upload')


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BaseConfig.PXYZ_UPLOAD_PATH, 'data-dev.db')


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BaseConfig.PXYZ_UPLOAD_PATH, 'data-test.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BaseConfig.PXYZ_UPLOAD_PATH, 'data.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
