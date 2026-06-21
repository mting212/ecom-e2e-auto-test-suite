# test_api_register.py（精简版 —— 删掉之前的 BASE_URL，改用 fixture）
"""注册接口自动化测试"""
import pytest


# ===== 成功注册 =====
def test_register_success(api_client, base_url):
    """完整合规注册 → 201"""
    resp = api_client.post(f"{base_url}/api/register", json={
        "phone": "13900139000",
        "password": "Aa123456",
        "confirm": "Aa123456",
    })
    assert resp.status_code == 201
    assert resp.json()["success"] is True


# ===== 手机号校验 =====
@pytest.mark.parametrize("phone, expected_msg", [
    ("",              "请输入手机号"),
    ("1390013900",    "手机号格式错误"),
    ("139001390000",  "手机号格式错误"),
    ("1390013900a",   "手机号格式错误"),
    ("13800001111",   "该手机号已被注册"),
])
def test_register_phone_invalid(api_client, base_url, phone, expected_msg):
    resp = api_client.post(f"{base_url}/api/register", json={
        "phone": phone,
        "password": "Aa123456",
        "confirm": "Aa123456",
    })
    assert resp.status_code == 400
    assert expected_msg in resp.json()["errors"]


# ===== 密码校验 =====
@pytest.mark.parametrize("password, expected_msg", [
    ("Abc1234",  "密码长度需8-20位"),
    ("12345678", "密码需包含字母和数字"),
    ("abcdefgh", "密码需包含字母和数字"),
])
def test_register_password_invalid(api_client, base_url, password,
expected_msg):
    resp = api_client.post(f"{base_url}/api/register", json={
        "phone": "13900139001",
        "password": password,
        "confirm": password,
    })
    assert resp.status_code == 400
    assert expected_msg in resp.json()["errors"]


# ===== 确认密码 =====
def test_register_confirm_mismatch(api_client, base_url):
    resp = api_client.post(f"{base_url}/api/register", json={
        "phone": "13900139002",
        "password": "Aa123456",
        "confirm": "Aa123457",
    })
    assert resp.status_code == 400
    assert "两次密码输入不一致" in resp.json()["errors"]


# ===== 多个错误同时存在 =====
def test_register_multiple_errors(api_client, base_url):
    resp = api_client.post(f"{base_url}/api/register", json={
        "phone": "",
        "password": "12345678",
        "confirm": "12345678",
    })
    assert resp.status_code == 400
    assert "请输入手机号" in resp.json()["errors"]
    assert "密码需包含字母和数字" in resp.json()["errors"]