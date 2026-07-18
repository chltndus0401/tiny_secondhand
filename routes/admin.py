from flask import Blueprint, request, redirect, url_for, flash, render_template, abort
from flask_login import login_required, current_user
from markupsafe import escape
from models.schema import db, Product, Report, User

admin_bp = Blueprint('admin', __name__)

# 시큐어코딩: 관리자 권한 검증 데코레이터 또는 함수
def admin_required():
    if current_user.username != 'admin':
        abort(403, description="관리자 권한이 필요합니다.")

@admin_bp.route('/report/<int:product_id>', methods=['GET', 'POST'])
@login_required
def report_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        reason = escape(request.form.get('reason', '').strip())
        if not reason:
            flash("신고 사유를 입력해주세요.", "error")
            return redirect(url_for('admin.report_product', product_id=product_id))
            
        new_report = Report(reporter_id=current_user.id, product_id=product.id, reason=reason)
        db.session.add(new_report)
        db.session.commit()
        
        flash("신고가 정상적으로 접수되었습니다. 관리자 검토 후 조치될 예정입니다.", "success")
        return redirect(url_for('product.product_detail', product_id=product_id))
        
    return render_template('report.html', product=product)

# 추가: 관리자 대시보드
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    admin_required()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin_dashboard.html', reports=reports)

# 추가: 악성 상품 강제 삭제
@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def force_delete_product(product_id):
    admin_required()
    product = Product.query.get_or_404(product_id)
    
    # 관련된 신고 내역 먼저 삭제 (외래키 제약조건 방지)
    Report.query.filter_by(product_id=product_id).delete()
    
    db.session.delete(product)
    db.session.commit()
    flash("관리자 권한으로 상품을 삭제했습니다.", "success")
    return redirect(url_for('admin.dashboard'))

# 추가: 악성 유저 영구 정지 (Ban)
@admin_bp.route('/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        flash("관리자 계정은 정지할 수 없습니다.", "error")
        return redirect(url_for('admin.dashboard'))
        
    user.is_banned = True
    db.session.commit()
    flash(f"{user.username} 계정이 정지되었습니다.", "success")
    return redirect(url_for('admin.dashboard'))