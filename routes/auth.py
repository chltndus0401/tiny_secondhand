import re
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.schema import db, User
RESTRICTED_USERNAMES = ['admin', 'root', 'system', 'administrator', 'manager']
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username.lower() in RESTRICTED_USERNAMES:
            flash("해당 아이디는 시스템 예약어로 사용할 수 없습니다.", "error")
            return redirect(url_for('auth.register'))

        if not re.match(PASSWORD_REGEX, password):
            flash("비밀번호는 영문, 숫자, 특수문자를 포함하여 8자리 이상이어야 합니다.", "error")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 아이디입니다.", "error")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요!", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # 시큐어코딩: 정지된 계정 접근 차단
            if user.is_banned:
                flash("관리자에 의해 이용이 정지된 계정입니다.", "error")
                return redirect(url_for('auth.login'))
                
            login_user(user)
            return redirect(url_for('product.list_products'))
        
        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('product.list_products'))

# --- 기존 코드 아래에 추가 ---

@auth_bp.route('/mypage', methods=['GET', 'POST'])
@login_required
def mypage():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # 시큐어코딩: 현재 비밀번호가 맞는지 검증 (계정 탈취 방어)
        if not check_password_hash(current_user.password_hash, current_password):
            flash("현재 비밀번호가 일치하지 않습니다.", "error")
            return redirect(url_for('auth.mypage'))

        # 시큐어코딩: 새 비밀번호 복잡도 검증
        if not re.match(r'^[a-zA-Z0-9]{5,}$', new_password):
            flash("새 비밀번호는 영문과 숫자만 사용하여 5자리 이상이어야 합니다.", "error")
            return redirect(url_for('auth.mypage'))

        # 시큐어코딩: 단방향 해시 암호화 후 저장
        current_user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        
        flash("비밀번호가 성공적으로 변경되었습니다.", "success")
        return redirect(url_for('auth.mypage'))

    return render_template('mypage.html')