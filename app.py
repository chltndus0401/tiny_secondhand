import os
from flask import Flask
from models.schema import db, User
from flask_login import LoginManager
from routes.auth import auth_bp
from routes.product import product_bp

def create_app():
    app = Flask(__name__)
    
    # 시큐어코딩: 하드코딩된 Secret Key 방지 및 랜덤 키 생성
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    # 시큐어코딩: SQL Injection 방지를 위한 ORM 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiny_shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Flask-Login 설정 (인증 관리)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/product')
    
    @app.route('/')
    def index():
        return "Tiny Second-hand Shopping Platform 서버 정상 작동 중!"

    # 앱 실행 시 테이블 자동 생성
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)