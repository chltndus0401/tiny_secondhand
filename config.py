import os

class Config:
    # 시큐어코딩: 하드코딩된 Secret Key 지양, 환경변수 사용
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secure-key'
    
    # Database 설정 예시
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tiny_shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False