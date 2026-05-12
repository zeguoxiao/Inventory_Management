def test_register_login_inventory_crud(client):
    # 注册
    r = client.post(
        "/register",
        data={
            "username": "demo_user",
            "password": "secret12",
            "password2": "secret12",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200

    # 登录
    r = client.post(
        "/login",
        data={"username": "demo_user", "password": "secret12"},
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "库存列表".encode("utf-8") in r.data or "暂无数据".encode("utf-8") in r.data

    # 新增
    r = client.post(
        "/products/add",
        data={
            "sku": "SKU001",
            "name": "测试商品",
            "category": "数码",
            "quantity": "10",
            "unit_price": "19.9",
            "note": "单元测试",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "测试商品".encode("utf-8") in r.data

    # 查询（模糊）
    r = client.get("/inventory?q=测试")
    assert r.status_code == 200
    assert "测试商品".encode("utf-8") in r.data

    # 修改：先取 id（简单解析 HTML 不可靠，这里用数据库）
    import db as db_mod

    conn = db_mod.get_connection()
    try:
        pid = conn.execute("SELECT id FROM products WHERE sku = ?", ("SKU001",)).fetchone()[
            "id"
        ]
    finally:
        conn.close()

    r = client.post(
        f"/products/{pid}/edit",
        data={
            "sku": "SKU001",
            "name": "测试商品改",
            "category": "数码",
            "quantity": "5",
            "unit_price": "9.99",
            "note": "已修改",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "测试商品改".encode("utf-8") in r.data

    # 删除
    r = client.post(f"/products/{pid}/delete", follow_redirects=True)
    assert r.status_code == 200


def test_login_validation_empty(client):
    r = client.post("/login", data={"username": "", "password": ""})
    assert r.status_code == 400
