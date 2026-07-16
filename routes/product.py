from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from markupsafe import escape
from models.schema import db, Product

product_bp = Blueprint('product', __name__)

@product_bp.route('/register', methods=['POST'])
@login_required
def register_product():
    data = request.get_json()
    
    # 시큐어코딩: XSS(크로스 사이트 스크립팅) 방지를 위한 입력값 이스케이프 처리
    title = escape(data.get('title', ''))
    description = escape(data.get('description', ''))
    price = data.get('price')

    if not title or not price:
        return jsonify({"error": "Title and price are required"}), 400

    new_product = Product(
        seller_id=current_user.id,
        title=title,
        description=description,
        price=int(price)
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product registered successfully", "product_id": new_product.id}), 201

@product_bp.route('/list', methods=['GET'])
def list_products():
    # ORM을 사용하므로 SQL Injection에 안전함
    products = Product.query.order_by(Product.created_at.desc()).all()
    result = [
        {"id": p.id, "title": p.title, "price": p.price, "seller_id": p.seller_id}
        for p in products
    ]
    return jsonify(result), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # 시큐어코딩: 부적절한 인가(IDOR) 방지 - 삭제 권한 검증
    if product.seller_id != current_user.id:
        return jsonify({"error": "Unauthorized to delete this product"}), 403

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

@product_bp.route('/search', methods=['GET'])
def search_product():
    keyword = request.args.get('q', '')
    # 시큐어코딩: ORM의 ilike를 사용하여 안전한 Parameterized Query 수행 (SQLi 방어)
    products = Product.query.filter(Product.title.ilike(f'%{keyword}%')).all()
    
    result = [{"id": p.id, "title": p.title, "price": p.price} for p in products]
    return jsonify(result), 200