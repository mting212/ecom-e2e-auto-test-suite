# test_api_products.py
"""商品接口自动化测试 —— 列表/搜索/筛选/详情"""
import pytest


# ============================================================
# 商品列表
# ============================================================

def test_get_all_products(api_client, base_url):
    """获取全部商品 → 返回6件预置商品"""
    resp = api_client.get(f"{base_url}/api/products")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["count"] == 6
    assert len(body["data"]) == 6


# ============================================================
# 关键词搜索
# ============================================================

@pytest.mark.parametrize("keyword, expected_count, expected_in_first", [
    ("iPhone", 1, "iPhone"),
    ("华为", 1, "华为"),
    ("Pro", 3, "Pro"),           # MacBook Pro + AirPods Pro + 华为 Mate 60 Pro
    ("xyz不存在的商品", 0, None),
])
def test_product_search(api_client, base_url, keyword, expected_count, expected_in_first):
    """关键词搜索 → 名称模糊匹配，不区分大小写"""
    resp = api_client.get(f"{base_url}/api/products?keyword={keyword}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == expected_count
    if expected_count > 0 and expected_in_first:
        assert expected_in_first.lower() in body["data"][0]["name"].lower()


# ============================================================
# 分类筛选
# ============================================================

def test_filter_by_category(api_client, base_url):
    """筛选分类'手机' → 返回3件（iPhone 15 + 华为 Mate 60 + 小米14 Ultra）"""
    resp = api_client.get(f"{base_url}/api/products?category=手机")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 3
    for item in body["data"]:
        assert item["category"] == "手机"


def test_filter_empty_category(api_client, base_url):
    """筛选不存在的分类 → 返回空列表"""
    resp = api_client.get(f"{base_url}/api/products?category=食品")
    assert resp.status_code == 200
    assert resp.json()["count"] == 0


# ============================================================
# 价格筛选
# ============================================================

def test_filter_by_price_range(api_client, base_url):
    """价格区间 1000-5000 → 返回 AirPods Pro(1899) + iPad Air(4799) + 小米14(4599) """
    resp = api_client.get(f"{base_url}/api/products?min_price=1000&max_price=5000")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 3  # AirPods Pro, iPad Air, 小米14 Ultra
    for item in body["data"]:
        assert 1000 <= item["price"] <= 5000


def test_filter_by_min_price_only(api_client, base_url):
    """只设最低价 10000 → 返回 MacBook Pro"""
    resp = api_client.get(f"{base_url}/api/products?min_price=10000")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["data"][0]["name"] == "MacBook Pro 14"


# ============================================================
# 组合筛选
# ============================================================

def test_combined_search_and_filter(api_client, base_url):
    """关键词'手机' + 分类'手机' + 价格 → 精确命中"""
    resp = api_client.get(
        f"{base_url}/api/products?keyword=小米&category=手机&min_price=4000&max_price=5000"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["data"][0]["name"] == "小米14 Ultra"


# ============================================================
# 商品详情
# ============================================================

def test_get_product_detail_exists(api_client, base_url):
    """查询存在的商品 → 返回完整字段"""
    resp = api_client.get(f"{base_url}/api/products/1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "iPhone 15"
    assert data["price"] == 5999
    assert data["stock"] == 100
    assert data["category"] == "手机"


def test_get_product_detail_not_exists(api_client, base_url):
    """查询不存在的商品 → 404"""
    resp = api_client.get(f"{base_url}/api/products/9999")
    assert resp.status_code == 404
    assert "商品不存在" in str(resp.json()["errors"])
