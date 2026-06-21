# api_server.py
"""ShopEasy 电商 API —— 给自动化测试当靶子

启动：python api_server.py
测试：pytest test_api_*.py -v

端点一览：
  POST /api/register       注册
  POST /api/login          登录
  GET  /api/products       商品列表 + 搜索
  GET  /api/products/<id>  商品详情
  POST /api/cart/add       加入购物车
  GET  /api/cart           查看购物车
  PUT  /api/cart/<id>      修改数量
  DELETE /api/cart/<id>    删除商品
  POST /api/orders         创建订单
  GET  /api/orders         订单列表
  POST /api/orders/<id>/pay      支付
  POST /api/orders/<id>/cancel   取消
  POST /api/test/clear     重置测试数据
"""

import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# 模拟数据库（内存存储）
# ============================================================

# 用户表：phone -> {password, nickname, created_at}
users: dict[str, dict] = {}

# 登录令牌：token -> phone
tokens: dict[str, str] = {}

# 商品表（预置数据）
products: list[dict] = [
    {"id": 1, "name": "iPhone 15", "category": "手机", "price": 5999, "stock": 100},
    {"id": 2, "name": "华为 Mate 60 Pro", "category": "手机", "price": 6999, "stock": 50},
    {"id": 3, "name": "MacBook Pro 14", "category": "电脑", "price": 14999, "stock": 30},
    {"id": 4, "name": "AirPods Pro", "category": "配件", "price": 1899, "stock": 200},
    {"id": 5, "name": "iPad Air", "category": "平板", "price": 4799, "stock": 80},
    {"id": 6, "name": "小米14 Ultra", "category": "手机", "price": 4599, "stock": 5},
]

# 购物车：phone -> [{product_id, quantity}]
carts: dict[str, list[dict]] = {}

# 订单表：order_id -> {phone, items, total, status, created_at}
orders: dict[str, dict] = {}

# 预置已注册手机号（用于"手机号已注册"测试场景）
SEED_PHONE = "13800001111"


def seed_data():
    """重置数据到初始状态"""
    global users, tokens, carts, orders
    users = {SEED_PHONE: {"password": "Aa123456", "nickname": "种子用户", "created_at": "2026-01-01"}}
    tokens = {}
    carts = {}
    orders = {}


seed_data()


# ============================================================
# 鉴权辅助
# ============================================================

def get_current_phone() -> str | None:
    """从 Authorization header 获取当前登录用户手机号"""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return tokens.get(auth[7:])
    return None


def login_required():
    """需要登录的接口调用此函数。返回 (phone, error_response)"""
    phone = get_current_phone()
    if not phone:
        return None, (jsonify({"success": False, "errors": ["请先登录"]}), 401)
    return phone, None


# ============================================================
# 用户模块
# ============================================================

@app.route("/api/register", methods=["POST"])
def register():
    """注册接口"""
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    confirm = data.get("confirm", "")
    nickname = data.get("nickname", "")

    errors = []

    # 手机号校验
    if not phone:
        errors.append("请输入手机号")
    elif len(phone) != 11 or not phone.isdigit():
        errors.append("手机号格式错误")
    elif phone in users:
        errors.append("该手机号已被注册")

    # 密码校验
    if len(password) < 8 or len(password) > 20:
        errors.append("密码长度需8-20位")
    else:
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        if not has_letter or not has_digit:
            errors.append("密码需包含字母和数字")

    # 确认密码
    if password != confirm:
        errors.append("两次密码输入不一致")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    users[phone] = {
        "password": password,
        "nickname": nickname or f"用户{phone[-4:]}",
        "created_at": datetime.now().isoformat(),
    }
    return jsonify({"success": True, "message": "注册成功"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    """登录接口，成功返回 token"""
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    errors = []

    if not phone:
        errors.append("请输入手机号")
    if not password:
        errors.append("请输入密码")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    user = users.get(phone)
    if not user:
        return jsonify({"success": False, "errors": ["账号不存在"]}), 401

    if user["password"] != password:
        return jsonify({"success": False, "errors": ["密码错误"]}), 401

    # 生成 token
    token = str(uuid.uuid4())
    tokens[token] = phone

    return jsonify({
        "success": True,
        "message": "登录成功",
        "token": token,
        "user": {"phone": phone, "nickname": user["nickname"]},
    }), 200


# ============================================================
# 商品模块
# ============================================================

@app.route("/api/products", methods=["GET"])
def get_products():
    """商品列表 + 搜索 + 筛选"""
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", type=float, default=0)
    max_price = request.args.get("max_price", type=float, default=float("inf"))

    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]
    if category:
        result = [p for p in result if p["category"] == category]
    if min_price > 0:
        result = [p for p in result if p["price"] >= min_price]
    if max_price != float("inf"):
        result = [p for p in result if p["price"] <= max_price]

    return jsonify({"success": True, "data": result, "count": len(result)}), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """商品详情"""
    for p in products:
        if p["id"] == product_id:
            return jsonify({"success": True, "data": p}), 200
    return jsonify({"success": False, "errors": ["商品不存在"]}), 404


# ============================================================
# 购物车模块
# ============================================================

@app.route("/api/cart", methods=["GET"])
def get_cart():
    """查看购物车"""
    phone, err = login_required()
    if err:
        return err

    cart_items = carts.get(phone, [])
    # 关联商品详情
    enriched = []
    for item in cart_items:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if product:
            enriched.append({
                "product_id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "subtotal": product["price"] * item["quantity"],
            })
    total = sum(e["subtotal"] for e in enriched)
    return jsonify({"success": True, "data": enriched, "total": total}), 200


@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    """加入购物车"""
    phone, err = login_required()
    if err:
        return err

    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # 参数校验
    if not product_id:
        return jsonify({"success": False, "errors": ["请提供商品ID"]}), 400
    if quantity < 1:
        return jsonify({"success": False, "errors": ["数量不能小于1"]}), 400

    # 商品是否存在
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"success": False, "errors": ["商品不存在"]}), 404

    # 库存检查
    if product["stock"] < quantity:
        return jsonify({"success": False, "errors": [f"库存不足，当前库存{product['stock']}件"]}), 400

    if phone not in carts:
        carts[phone] = []

    # 检查购物车是否已有同商品
    existing = next((item for item in carts[phone] if item["product_id"] == product_id), None)
    if existing:
        new_qty = existing["quantity"] + quantity
        if product["stock"] < new_qty:
            return jsonify({"success": False, "errors": [f"库存不足，购物车已有{existing['quantity']}件，加购{quantity}件超出库存"]}), 400
        existing["quantity"] = new_qty
    else:
        carts[phone].append({"product_id": product_id, "quantity": quantity})

    return jsonify({"success": True, "message": "已加入购物车"}), 200


@app.route("/api/cart/<int:product_id>", methods=["PUT"])
def update_cart_item(product_id):
    """修改购物车商品数量"""
    phone, err = login_required()
    if err:
        return err

    data = request.get_json() or {}
    quantity = data.get("quantity", 1)

    if phone not in carts:
        return jsonify({"success": False, "errors": ["购物车为空"]}), 404

    item = next((item for item in carts[phone] if item["product_id"] == product_id), None)
    if not item:
        return jsonify({"success": False, "errors": ["购物车中无此商品"]}), 404

    if quantity <= 0:
        carts[phone].remove(item)
        return jsonify({"success": True, "message": "商品已从购物车移除"}), 200

    product = next((p for p in products if p["id"] == product_id), None)
    if product and product["stock"] < quantity:
        return jsonify({"success": False, "errors": [f"库存不足，当前库存{product['stock']}件"]}), 400

    item["quantity"] = quantity
    return jsonify({"success": True, "message": "数量已更新"}), 200


@app.route("/api/cart/<int:product_id>", methods=["DELETE"])
def remove_from_cart(product_id):
    """从购物车删除商品"""
    phone, err = login_required()
    if err:
        return err

    if phone not in carts:
        return jsonify({"success": False, "errors": ["购物车为空"]}), 404

    item = next((item for item in carts[phone] if item["product_id"] == product_id), None)
    if not item:
        return jsonify({"success": False, "errors": ["购物车中无此商品"]}), 404

    carts[phone].remove(item)
    return jsonify({"success": True, "message": "商品已从购物车移除"}), 200


# ============================================================
# 订单模块
# ============================================================

@app.route("/api/orders", methods=["POST"])
def create_order():
    """创建订单（从购物车结算）"""
    phone, err = login_required()
    if err:
        return err

    cart_items = carts.get(phone, [])
    if not cart_items:
        return jsonify({"success": False, "errors": ["购物车为空，无法下单"]}), 400

    # 构建订单项
    order_items = []
    for item in cart_items:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if not product:
            continue
        if product["stock"] < item["quantity"]:
            return jsonify({
                "success": False,
                "errors": [f"{product['name']}库存不足，当前库存{product['stock']}件"]
            }), 400
        order_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
        })
        # 扣库存
        product["stock"] -= item["quantity"]

    total = sum(i["price"] * i["quantity"] for i in order_items)
    order_id = str(uuid.uuid4())[:8]

    orders[order_id] = {
        "order_id": order_id,
        "phone": phone,
        "items": order_items,
        "total": total,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    # 清空购物车
    carts[phone] = []

    return jsonify({
        "success": True,
        "message": "下单成功",
        "data": orders[order_id],
    }), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """订单列表"""
    phone, err = login_required()
    if err:
        return err

    my_orders = [o for o in orders.values() if o["phone"] == phone]
    # 按时间倒序
    my_orders.sort(key=lambda o: o["created_at"], reverse=True)

    return jsonify({"success": True, "data": my_orders, "count": len(my_orders)}), 200


@app.route("/api/orders/<order_id>/pay", methods=["POST"])
def pay_order(order_id):
    """支付订单（Mock）"""
    phone, err = login_required()
    if err:
        return err

    order = orders.get(order_id)
    if not order:
        return jsonify({"success": False, "errors": ["订单不存在"]}), 404
    if order["phone"] != phone:
        return jsonify({"success": False, "errors": ["无权操作此订单"]}), 403
    if order["status"] != "pending":
        return jsonify({"success": False, "errors": [f"当前状态'{order['status']}'不可支付"]}), 400

    # 模拟支付（90%成功率）
    import random
    if random.random() < 0.9:
        order["status"] = "paid"
        order["paid_at"] = datetime.now().isoformat()
        return jsonify({"success": True, "message": "支付成功"}), 200
    else:
        return jsonify({"success": False, "errors": ["支付失败，请重试"]}), 500


@app.route("/api/orders/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    """取消订单"""
    phone, err = login_required()
    if err:
        return err

    order = orders.get(order_id)
    if not order:
        return jsonify({"success": False, "errors": ["订单不存在"]}), 404
    if order["phone"] != phone:
        return jsonify({"success": False, "errors": ["无权操作此订单"]}), 403
    if order["status"] not in ("pending",):
        return jsonify({"success": False, "errors": [f"当前状态'{order['status']}'不可取消"]}), 400

    # 恢复库存
    for item in order["items"]:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if product:
            product["stock"] += item["quantity"]

    order["status"] = "cancelled"
    return jsonify({"success": True, "message": "订单已取消"}), 200


# ============================================================
# 测试辅助
# ============================================================

@app.route("/api/test/clear", methods=["POST"])
def clear_test_data():
    """重置所有数据到初始状态"""
    seed_data()
    return jsonify({"success": True, "message": "测试数据已重置"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
