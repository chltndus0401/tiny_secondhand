import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("Critical Security Error: 환경 변수에 SECRET_KEY가 설정되지 않았습니다.")