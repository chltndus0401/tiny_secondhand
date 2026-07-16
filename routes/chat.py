from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/<int:target_user_id>', methods=['GET'])
def get_chat_history(target_user_id):
    # TODO: 현재 로그인한 유저와 특정 유저 간의 대화 내역 조회 (접근 권한 검증 필수)
    pass

@chat_bp.route('/send', methods=['POST'])
def send_message():
    # TODO: 채팅 메시지 전송 및 저장
    # 보안 주의: XSS(교차 사이트 스크립팅) 방지를 위해 메시지 입력값 검증 및 이스케이프 처리
    pass