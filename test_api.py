# test_api.py
"""接口测试 —— 使用 httpbin.org 作为练习靶场"""
import requests


# ===== GET 请求 =====
def test_get_basic():
    """最基本的 GET 请求"""
    resp = requests.get("https://httpbin.org/get?name=test&page=1")
    assert resp.status_code == 200           # 断言状态码
    data = resp.json()                       # 把 JSON 响应体转成 dict
    assert data["args"]["name"] == "test"    # 断言传的参数正确
    assert data["args"]["page"] == "1"


# ===== POST 请求（JSON 体）=====
def test_post_json():
    """POST 请求，发 JSON 数据"""
    body = {"username": "admin", "password": "123456"}
    resp = requests.post("https://httpbin.org/post", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["json"]["username"] == "admin"


# ===== 状态码断言 =====
def test_404():
    """请求不存在的路径 → 应返回 404"""
    resp = requests.get("https://httpbin.org/status/404")
    assert resp.status_code == 404


# ===== 响应头断言 =====
def test_content_type():
    """返回的 Content-Type 应该是 application/json"""
    resp = requests.get("https://httpbin.org/json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["Content-Type"]

def test_status_fail_demo():
    """故意写错预期 → 看 pytest 怎么报 FAILED"""
    resp = requests.get("https://httpbin.org/get")
    assert resp.status_code == 200  # 实际是 200，故意写错