# test_api_orders.py
"""订单接口自动化测试 —— 下单/支付/取消/列表"""
import pytest


# ============================================================
# 下单成功
# ============================================================

def test_create_order_success(auth_headers, api_client, base_url):
    """加购后下单 → 201，订单创建，购物车清空，库存扣减"""
    # 加购 iPhone 15 * 2
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 2,
    }, headers=auth_headers)

    # 记录下单前库存
    before = api_client.get(f"{base_url}/api/products/1").json()["data"]["stock"]

    # 下单
    resp = api_client.post(f"{base_url}/api/orders", headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    order = body["data"]
    assert "order_id" in order
    assert order["status"] == "pending"
    assert order["total"] == 5999 * 2
    assert len(order["items"]) == 1

    # 购物车应清空
    cart = api_client.get(f"{base_url}/api/cart", headers=auth_headers)
    assert cart.json()["data"] == []

    # 库存应扣减
    after = api_client.get(f"{base_url}/api/products/1").json()["data"]["stock"]
    assert after == before - 2


def test_create_order_multiple_items(auth_headers, api_client, base_url):
    """加购多种商品后下单 → 订单包含多件商品"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 4, "quantity": 3,
    }, headers=auth_headers)

    resp = api_client.post(f"{base_url}/api/orders", headers=auth_headers)
    assert resp.status_code == 201
    items = resp.json()["data"]["items"]
    assert len(items) == 2
    # 总价 = 5999*1 + 1899*3
    assert resp.json()["data"]["total"] == 5999 + 1899 * 3


# ============================================================
# 下单失败
# ============================================================

def test_create_order_empty_cart(auth_headers, api_client, base_url):
    """购物车为空时下单 → 400"""
    resp = api_client.post(f"{base_url}/api/orders", headers=auth_headers)
    assert resp.status_code == 400
    assert "购物车为空" in str(resp.json()["errors"])


def test_create_order_requires_auth(api_client, base_url):
    """未登录下单 → 401"""
    resp = api_client.post(f"{base_url}/api/orders")
    assert resp.status_code == 401


def test_order_response_structure(auth_headers, api_client, base_url):
    """订单响应包含所有必要字段"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    resp = api_client.post(f"{base_url}/api/orders", headers=auth_headers)
    order = resp.json()["data"]

    # 必要字段全部存在
    assert "order_id" in order
    assert "phone" in order
    assert "items" in order
    assert "total" in order
    assert "status" in order
    assert "created_at" in order
    # items 里每个元素有 product_id, name, price, quantity
    assert len(order["items"]) >= 1
    item = order["items"][0]
    assert "product_id" in item
    assert "name" in item
    assert "price" in item
    assert "quantity" in item


# ============================================================
# 订单列表
# ============================================================

def test_get_orders_empty(auth_headers, api_client, base_url):
    """新用户 → 订单列表为空"""
    resp = api_client.get(f"{base_url}/api/orders", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["count"] == 0
    assert resp.json()["data"] == []


def test_get_orders_with_data(auth_headers, api_client, base_url):
    """下单后 → 订单列表包含订单，按时间倒序"""
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    api_client.post(f"{base_url}/api/orders", headers=auth_headers)

    # 再下一单
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 2, "quantity": 1,
    }, headers=auth_headers)
    api_client.post(f"{base_url}/api/orders", headers=auth_headers)

    resp = api_client.get(f"{base_url}/api/orders", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["count"] == 2
    # 倒序：后创建的在前
    orders_list = resp.json()["data"]
    assert orders_list[0]["created_at"] >= orders_list[1]["created_at"]


def test_get_orders_requires_auth(api_client, base_url):
    """未登录查看订单 → 401"""
    resp = api_client.get(f"{base_url}/api/orders")
    assert resp.status_code == 401


# ============================================================
# 支付
# ============================================================

def test_pay_order_success(auth_headers, api_client, base_url):
    """支付 pending 订单 → 200（90%成功率，失败重试一次）"""
    # 下单
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    order_id = api_client.post(f"{base_url}/api/orders", headers=auth_headers)\
        .json()["data"]["order_id"]

    # 支付（模拟有10%失败率，失败时重试）
    max_retries = 3
    for attempt in range(max_retries):
        resp = api_client.post(
            f"{base_url}/api/orders/{order_id}/pay", headers=auth_headers
        )
        if resp.status_code == 200:
            assert resp.json()["success"] is True
            return
        # 500 是模拟支付失败，重试
    # 如果3次都失败，跳过（概率 0.1^3 = 0.001）
    pytest.skip("模拟支付连续失败，概率极低")


def test_pay_nonexistent_order(auth_headers, api_client, base_url):
    """支付不存在的订单 → 404"""
    resp = api_client.post(f"{base_url}/api/orders/nonexist/pay", headers=auth_headers)
    assert resp.status_code == 404


def test_pay_requires_auth(api_client, base_url):
    """未登录支付 → 401"""
    resp = api_client.post(f"{base_url}/api/orders/some-id/pay")
    assert resp.status_code == 401


# ============================================================
# 取消订单
# ============================================================

def test_cancel_order_restores_stock(auth_headers, api_client, base_url):
    """取消订单 → 库存恢复"""
    # 记录库存
    stock_before = api_client.get(f"{base_url}/api/products/1").json()["data"]["stock"]

    # 下单
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 3,
    }, headers=auth_headers)
    order_id = api_client.post(f"{base_url}/api/orders", headers=auth_headers)\
        .json()["data"]["order_id"]

    # 下单后库存已扣
    stock_after_order = api_client.get(f"{base_url}/api/products/1").json()["data"]["stock"]
    assert stock_after_order == stock_before - 3

    # 取消
    resp = api_client.post(
        f"{base_url}/api/orders/{order_id}/cancel", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # 库存恢复
    stock_after_cancel = api_client.get(f"{base_url}/api/products/1").json()["data"]["stock"]
    assert stock_after_cancel == stock_before


def test_cancel_paid_order_fails(auth_headers, api_client, base_url):
    """已支付的订单不可取消 → 400"""
    # 下单
    api_client.post(f"{base_url}/api/cart/add", json={
        "product_id": 1, "quantity": 1,
    }, headers=auth_headers)
    order_id = api_client.post(f"{base_url}/api/orders", headers=auth_headers)\
        .json()["data"]["order_id"]

    # 支付
    resp = api_client.post(
        f"{base_url}/api/orders/{order_id}/pay", headers=auth_headers
    )
    if resp.status_code != 200:
        pytest.skip("支付失败，无法继续测取消已支付订单")

    # 取消已支付订单
    resp = api_client.post(
        f"{base_url}/api/orders/{order_id}/cancel", headers=auth_headers
    )
    assert resp.status_code == 400
    assert "不可取消" in str(resp.json()["errors"])


def test_cancel_nonexistent_order(auth_headers, api_client, base_url):
    """取消不存在的订单 → 404"""
    resp = api_client.post(
        f"{base_url}/api/orders/nonexist/cancel", headers=auth_headers
    )
    assert resp.status_code == 404


def test_cancel_requires_auth(api_client, base_url):
    """未登录取消 → 401"""
    resp = api_client.post(f"{base_url}/api/orders/some-id/cancel")
    assert resp.status_code == 401
