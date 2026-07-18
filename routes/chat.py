from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from markupsafe import escape
from models.schema import db, Product, ChatRoom, Message, User

chat_bp = Blueprint('chat', __name__)

# ★ 새롭게 추가된 내 채팅 목록 라우트
@chat_bp.route('/list')
@login_required
def my_chats():
    # 내가 구매자이거나 판매자인 채팅방 모두 가져오기
    rooms = ChatRoom.query.filter(or_(ChatRoom.buyer_id == current_user.id, ChatRoom.seller_id == current_user.id)).all()
    
    chat_data = []
    for room in rooms:
        other_user_id = room.seller_id if current_user.id == room.buyer_id else room.buyer_id
        other_user = User.query.get(other_user_id)
        
        # 가장 최근 메시지 가져오기 (목록에서 미리보기용)
        last_message = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.desc()).first()
        
        chat_data.append({
            'room': room,
            'other_user': other_user,
            'last_message': last_message
        })
        
    return render_template('chat_list.html', chat_data=chat_data)

@chat_bp.route('/start/<int:product_id>')
@login_required
def start_chat(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == current_user.id:
        flash("자신의 상품에는 채팅을 걸 수 없습니다.", "error")
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    room = ChatRoom.query.filter_by(product_id=product_id, buyer_id=current_user.id).first()
    if not room:
        room = ChatRoom(product_id=product_id, buyer_id=current_user.id, seller_id=product.seller_id)
        db.session.add(room)
        db.session.commit()
        
    return redirect(url_for('chat.room', room_id=room.id))

@chat_bp.route('/room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    
    if current_user.id not in (room.buyer_id, room.seller_id):
        flash("이 채팅방에 접근할 권한이 없습니다.", "error")
        return redirect(url_for('product.list_products'))
        
    if request.method == 'POST':
        content = escape(request.form.get('content', '').strip())
        if content:
            new_msg = Message(room_id=room.id, sender_id=current_user.id, content=content)
            db.session.add(new_msg)
            db.session.commit()
        return redirect(url_for('chat.room', room_id=room.id))
        
    messages = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.asc()).all()
    other_user_id = room.seller_id if current_user.id == room.buyer_id else room.buyer_id
    other_user = User.query.get(other_user_id)
    
    return render_template('chat_room.html', room=room, messages=messages, other_user=other_user)