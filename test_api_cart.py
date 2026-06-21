# test_api_cart.py
"""购物车接口自动化测试 —— 覆盖 test_cases.md 五、购物车（10条）"""

import pytest


# ============================================================
# 加入购物车
# ============================================================

def test_add_to_cart_success(auth_headers, api_client, base_url):
    """TC-CART-EC-01: 登录后加入购物车 → 200"""
    resp = api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1,
        "quantity": 2,
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_add_to_cart_then_verify(auth_headers, api_client, base_url):
    """加购后查看购物车 → 商品存在，数量正确，小计正确"""
    # 加购
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1,
        "quantity": 2,
    }, headers=auth_headers)
    # 查看
    resp = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["data"]
    assert len(items) == 1
    assert items[0]["product_id"] == 1
    assert items[0]["quantity"] == 2
    assert items[0]["subtotal"] == 5999 * 2  # iPhone 15单价


def test_add_to_cart_quantity_zero(auth_headers, api_client, base_url):
    """TC-CART-EC-04: 数量为0 → 400"""
    resp = api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1,
        "quantity": 0,
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_add_to_cart_product_not_exist(auth_headers, api_client, base_url):
    """商品不存在 → 404"""
    resp = api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 9999,
        "quantity": 1,
    }, headers=auth_headers)
    assert resp.status_code == 404


def test_add_to_cart_stock_insufficient(auth_headers, api_client, base_url):
    """TC-CART-SC-02: 加购数量超过库存 → 400 + 库存不足提示"""
    # 小米14 Ultra 只有5件库存
    resp = api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 6,
        "quantity": 100,
    }, headers=auth_headers)
    assert resp.status_code == 400
    assert "库存不足" in str(resp.json()["errors"])


def test_add_to_cart_duplicate_product(auth_headers, api_client, base_url):
    """同一商品加购两次 → 数量合并，不创建重复条目"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 2,
    }, headers=auth_headers)
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 3,
    }, headers=auth_headers)
    # 验证
    resp = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    items = resp.json()["data"]
    assert len(items) == 1  # 只有一条
    assert items[0]["quantity"] == 5  # 数量合并


# ============================================================
# 修改购物车
# ============================================================

def test_update_cart_quantity(auth_headers, api_client, base_url):
    """TC-CART-EC-02: 修改数量 → 200，数量和金额更新"""
    # 先加购
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    # 修改
    resp = api_client.put(f"{base_url}/api/cart/1", json={
        "quantity": 3,
    }, headers=auth_headers)
    assert resp.status_code == 200
    # 验证
    cart = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    item = cart.json()["data"][0]
    assert item["quantity"] == 3


def test_update_cart_to_zero_removes_item(auth_headers, api_client, base_url):
    """TC-CART-EC-03: 数量改为0 → 商品从购物车移除"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    resp = api_client.put(f"{base_url}/api/cart/1", json={
        "quantity": 0,
    }, headers=auth_headers)
    assert resp.status_code == 200
    # 验证购物车为空
    cart = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    assert cart.json()["data"] == []


# ============================================================
# 删除购物车
# ============================================================

def test_delete_cart_item(auth_headers, api_client, base_url):
    """TC-CART-EC-06: 删除商品 → 200，购物车无该商品"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    resp = api_client.delete(f"{base_url}/api/cart/1", headers=auth_headers)
    assert resp.status_code == 200
    # 验证
    cart = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    assert cart.json()["data"] == []


def test_delete_nonexistent_item(auth_headers, api_client, base_url):
    """删除购物车中不存在的商品 → 404"""
    resp = api_client.delete(f"{base_url}/api/cart/9999", headers=auth_headers)
    assert resp.status_code == 404


# ============================================================
# 未登录访问
# ============================================================

def test_cart_requires_auth(api_client, base_url):
    """未登录访问购物车 → 401"""
    resp = api_client.get(f"{base_url}/api/cart")
    assert resp.status_code == 401
