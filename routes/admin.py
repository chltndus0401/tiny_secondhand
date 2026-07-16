from flask import Blueprint, request, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/report', methods=['POST'])
def submit_report():
    # TODO: 불량 상품 또는 악성 유저 신고 접수 (신고 사유 포함)
    pass

@admin_bp.route('/reports', methods=['GET'])
def list_reports():
    # TODO: 접수된 신고 목록 조회 (관리자 권한 인가 검증 철저히 수행)
    pass

@admin_bp.route('/action', methods=['POST'])
def auto_ban_action():
    # TODO: 자동 제재 로직 구현 (예: 특정 유저에 대한 신고가 N회 누적될 경우 계정 정지 처리)
    pass