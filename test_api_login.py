# test_api_login.py
"""登录接口自动化测试 —— 覆盖 test_cases.md 二、用户登录（12条）"""

import pytest


# ============================================================
# 登录成功
# ============================================================

def test_login_success(api_client, base_url, valid_register_data):
    """TC-LOG-EC-01: 正确手机号+正确密码 → 200 + token"""
    # 先注册
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    # 登录
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": valid_register_data["phone"],
        "password": valid_register_data["password"],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "token" in body
    assert len(body["token"]) > 0


# ============================================================
# 登录失败 —— 等价类 + 判定表
# ============================================================

@pytest.mark.parametrize("phone, password, expected_status, expected_msg", [
    # TC-LOG-EC-02: 已注册手机号 + 错误密码 → 401
    # 13800001111 是种子数据，始终存在
    ("13800001111", "WrongPass12", 401, "密码错误"),
    # TC-LOG-EC-03: 未注册手机号 → 401
    ("13999999999", "Aa123456", 401, "账号不存在"),
    # TC-LOG-EC-04: 手机号为空 → 400
    ("", "Aa123456", 400, "请输入手机号"),
    # TC-LOG-EC-05: 密码为空 → 400
    ("13800001111", "", 400, "请输入密码"),
])
def test_login_fail(api_client, base_url, phone, password,
                    expected_status, expected_msg):
    """登录失败场景 —— 参数化覆盖4种失败情况"""
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": phone,
        "password": password,
    })
    assert resp.status_code == expected_status
    assert expected_msg in str(resp.json()["errors"])


# ============================================================
# 错误推测
# ============================================================

def test_login_sql_injection(api_client, base_url):
    """TC-LOG-EG-01: SQL注入 → 登录失败，不暴露数据库错误"""
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": "admin'--",
        "password": "anything",
    })
    assert resp.status_code in (400, 401)
    # 关键：错误信息不应包含数据库关键字
    body_str = str(resp.json())
    assert "SQL" not in body_str.upper()
    assert "syntax" not in body_str.lower()


def test_login_case_sensitive(api_client, base_url, valid_register_data):
    """TC-LOG-EG-02: 密码区分大小写"""
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    # 用大写版本的正确密码
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": valid_register_data["phone"],
        "password": valid_register_data["password"].upper(),  # AA123456
    })
    assert resp.status_code == 401
    assert "密码错误" in str(resp.json()["errors"])


# ============================================================
# 场景法
# ============================================================

def test_login_get_token_in_response(api_client, base_url,
                                     valid_register_data):
    """TC-LOG-HT-01: 登录成功后 token 在 response body 中返回"""
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": valid_register_data["phone"],
        "password": valid_register_data["password"],
    })
    token = resp.json()["token"]
    # 用 token 访问需要鉴权的接口
    cart_resp = api_client.get(f"{base_url}/api/cart", headers={
        "Authorization": f"Bearer {token}",
    })
    assert cart_resp.status_code == 200  # 未鉴权会返回401


def test_login_returns_user_info(api_client, base_url, valid_register_data):
    """登录成功应返回用户基本信息（phone + nickname）"""
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": valid_register_data["phone"],
        "password": valid_register_data["password"],
    })
    user = resp.json()["user"]
    assert user["phone"] == valid_register_data["phone"]
    assert "nickname" in user


def test_unauthorized_access_returns_401(api_client, base_url):
    """未登录访问购物车 → 401"""
    resp = api_client.get(f"{base_url}/api/cart")
    assert resp.status_code == 401
    assert "请先登录" in str(resp.json()["errors"])


# ============================================================
# 连续错误登录不锁定基础验证
# ============================================================

def test_multiple_wrong_passwords(api_client, base_url, valid_register_data):
    """同一账号连续3次输错 → 每次都应返回401（不测试锁定，因为当前实现无锁定）"""
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    for _ in range(3):
        resp = api_client.post(f"{base_url}/api/login", json={
            "phone": valid_register_data["phone"],
            "password": "WrongPassword1",
        })
        assert resp.status_code == 401
