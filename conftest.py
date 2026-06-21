# conftest.py
"""共享 fixture：所有测试文件自动发现此文件中的 fixture"""

import pytest
import requests
import random
import subprocess
import time
import os
import signal


# ============================================================
# 服务器管理
# ============================================================

@pytest.fixture(scope="session")
def base_url():
    """Flask 测试服务器地址"""
    return "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def api_client():
    """复用 requests.Session —— 连接复用 + Cookie 自动管理"""
    session = requests.Session()
    yield session
    session.close()


# ============================================================
# 数据清理（每个测试前后自动执行）
# ============================================================

@pytest.fixture(autouse=True)
def reset_test_data(api_client, base_url):
    """
    每个测试前后重置服务器数据。
    autouse=True → 所有测试自动调用，不需要显式声明。
    """
    try:
        api_client.post(f"{base_url}/api/test/clear", timeout=3)
    except requests.ConnectionError:
        pass  # 服务器没启动时不阻塞
    yield
    try:
        api_client.post(f"{base_url}/api/test/clear", timeout=3)
    except requests.ConnectionError:
        pass


# ============================================================
# 测试数据生成
# ============================================================

@pytest.fixture
def fresh_phone():
    """每次生成一个随机未注册手机号，避免测试数据冲突"""
    return f"139{random.randint(10000000, 99999999)}"


@pytest.fixture
def valid_register_data(fresh_phone):
    """一组合规的注册数据"""
    return {
        "phone": fresh_phone,
        "password": "Aa123456",
        "confirm": "Aa123456",
    }


@pytest.fixture
def auth_headers(api_client, base_url, valid_register_data):
    """
    注册一个新用户并登录，返回带 Authorization 的 headers。
    需要登录态的测试直接使用这个 fixture。
    """
    # 先注册
    api_client.post(f"{base_url}/api/register", json=valid_register_data)
    # 再登录获取 token
    resp = api_client.post(f"{base_url}/api/login", json={
        "phone": valid_register_data["phone"],
        "password": valid_register_data["password"],
    })
    token = resp.json().get("token", "")
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# Session 结束后的清理钩子
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """所有测试跑完后执行——可用于关闭服务器等清理"""
    pass
