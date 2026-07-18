import os
import uuid
from flask import Blueprint, request, render_template, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from markupsafe import escape
from models.schema import db, Product, User

product_bp = Blueprint('product', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/', methods=['GET'])
def list_products():
    query = request.args.get('q', '').strip()
    if query:
        # 시큐어코딩: ORM을 이용한 파라미터화된 쿼리 (SQL 인젝션 방어)
        products = Product.query.filter(Product.title.ilike(f'%{query}%')).order_by(Product.created_at.desc()).all()
    else:
        products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('index.html', products=products, query=query)

@product_bp.route('/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    seller = User.query.get(product.seller_id)
    return render_template('detail.html', product=product, seller=seller)

@product_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_product():
    if request.method == 'POST':
        title = escape(request.form.get('title', ''))
        description = escape(request.form.get('description', ''))
        price = request.form.get('price')
        file = request.files.get('image')

        if not title or not price:
            flash("상품명과 가격은 필수입니다.", "error")
            return redirect(url_for('product.register_product'))

        filename = None
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        elif file and file.filename != '':
            flash("허용되지 않는 파일 형식입니다.", "error")
            return redirect(url_for('product.register_product'))

        new_product = Product(
            seller_id=current_user.id,
            title=title,
            description=description,
            price=int(price),
            image_filename=filename
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('product.list_products'))

    return render_template('create.html')

# 추가: 상품 수정 기능
@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # 시큐어코딩: 인가(Authorization) 검증 - 작성자 본인만 수정 가능
    if product.seller_id != current_user.id:
        abort(403, description="수정 권한이 없습니다.")

    if request.method == 'POST':
        product.title = escape(request.form.get('title', ''))
        product.description = escape(request.form.get('description', ''))
        product.price = int(request.form.get('price'))
        file = request.files.get('image')

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            product.image_filename = filename

        db.session.commit()
        flash("상품이 수정되었습니다.", "success")
        return redirect(url_for('product.product_detail', product_id=product.id))

    return render_template('edit.html', product=product)

# 추가: 상품 삭제 기능
@product_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # 시큐어코딩: 인가(Authorization) 검증 - 작성자 본인만 삭제 가능
    if product.seller_id != current_user.id:
        abort(403, description="삭제 권한이 없습니다.")
        
    db.session.delete(product)
    db.session.commit()
    flash("상품이 성공적으로 삭제되었습니다.", "success")
    return redirect(url_for('product.list_products'))