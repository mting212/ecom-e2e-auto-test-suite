# test_api.py
"""接口测试 —— 使用 httpbin.org 作为练习靶场"""
import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope="module")
def http():
    """共享 Session"""
    session = requests.Session()
    session.verify = False
    yield session
    session.close()


# httpbin.org 当前 503，暂时跳过
pytestmark = pytest.mark.skip(reason="httpbin.org 服务不可用，等待恢复")


def test_get_basic(http):
    resp = http.get("https://httpbin.org/get?name=test&page=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["args"]["name"] == "test"
    assert data["args"]["page"] == "1"


def test_post_json(http):
    body = {"username": "admin", "password": "123456"}
    resp = http.post("https://httpbin.org/post", json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["json"]["username"] == "admin"


def test_404(http):
    resp = http.get("https://httpbin.org/status/404")
    assert resp.status_code == 404


def test_content_type(http):
    resp = http.get("https://httpbin.org/json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["Content-Type"]


def test_status_fail_demo(http):
    resp = http.get("https://httpbin.org/get")
    assert resp.status_code == 200
