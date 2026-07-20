import os
import secrets
from flask import Flask, session, request, abort, redirect, url_for
from models.schema import db, User
from flask_login import LoginManager
from routes.auth import auth_bp
from routes.product import product_bp
from routes.chat import chat_bp      # 채팅 라우트 추가
from routes.admin import admin_bp    # 관리자(신고) 라우트 추가

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(24))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiny_shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "로그인이 필요한 서비스입니다."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def csrf_protect():
        if request.method in ("POST", "PUT", "DELETE"):
            token = session.get('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                abort(403, description="CSRF 검증에 실패했습니다. 비정상적인 접근입니다.")

    def generate_csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        return session['_csrf_token']
    app.jinja_env.globals['csrf_token'] = generate_csrf_token

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return redirect(url_for('product.list_products'))

    with app.app_context():
        db.create_all()


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)