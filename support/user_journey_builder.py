"""Build conservative, source-backed login/registration journeys."""
from .code_explorer import explore

STEPS = {
    "login": [
        "Mở https://dm.kcb.vn và chọn mục đăng nhập.",
        "Nếu có Gmail, chọn Tiếp tục với Google và chọn tài khoản của bạn.",
        "Nếu đã được cấp tài khoản không dùng Google, nhập tên đăng nhập và mật khẩu.",
        "Nếu hệ thống yêu cầu kích hoạt hoặc chưa có quyền, thực hiện hướng dẫn trên màn hình.",
    ],
    "register": [
        "Mở https://dm.kcb.vn và chọn Đăng ký tại khu vực tài khoản.",
        "Chọn luồng đăng ký phù hợp: Gmail hoặc chuyên gia theo yêu cầu của đơn vị.",
        "Điền thông tin được yêu cầu; hồ sơ chuyên gia có thể cần công văn.",
        "Gửi đăng ký và chờ xét duyệt/kích hoạt trước khi truy cập chức năng có phân quyền.",
    ],
}

def build_journey(root, topic):
    evidence = explore(root, topic)
    if not evidence:
        return {"status": "insufficient_evidence", "topic": topic, "steps": [],
                "evidence": [], "review_required": True}
    return {"status": "draft_needs_review", "topic": topic, "steps": STEPS[topic],
            "evidence": evidence, "review_required": True}
