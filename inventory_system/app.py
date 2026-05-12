from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import close_db, db_conn, init_db

app = Flask(__name__)
app.secret_key = "change-me-in-production-use-env"  # 实训演示：正式环境请改为环境变量
app.teardown_appcontext(close_db)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def root():
    if session.get("user_id"):
        return redirect(url_for("inventory"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            flash("用户名和密码不能为空。", "error")
            return render_template("login.html"), 400
        conn = db_conn()
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if not row or not check_password_hash(row["password_hash"], password):
            flash("用户名或密码错误。", "error")
            return render_template("login.html"), 401
        session.clear()
        session["user_id"] = row["id"]
        session["username"] = username
        flash("登录成功。", "success")
        return redirect(url_for("inventory"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""
        if not username or not password:
            flash("用户名和密码不能为空。", "error")
            return render_template("register.html"), 400
        if password != password2:
            flash("两次输入的密码不一致。", "error")
            return render_template("register.html"), 400
        if len(username) < 3:
            flash("用户名至少 3 个字符。", "error")
            return render_template("register.html"), 400
        if len(password) < 6:
            flash("密码至少 6 位。", "error")
            return render_template("register.html"), 400
        conn = db_conn()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?,?,?)",
                (username, generate_password_hash(password), _now_iso()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("该用户名已被注册。", "error")
            return render_template("register.html"), 409
        flash("注册成功，请登录。", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("已退出登录。", "success")
    return redirect(url_for("login"))


def _require_login():
    if not session.get("user_id"):
        flash("请先登录。", "error")
        return redirect(url_for("login"))
    return None


@app.route("/inventory")
def inventory():
    redir = _require_login()
    if redir:
        return redir
    q = (request.args.get("q") or "").strip()
    conn = db_conn()
    if q:
        like = f"%{q}%"
        rows = conn.execute(
            """
            SELECT * FROM products
            WHERE sku LIKE ? OR name LIKE ? OR category LIKE ? OR note LIKE ?
            ORDER BY updated_at DESC, id DESC
            """,
            (like, like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY updated_at DESC, id DESC"
        ).fetchall()
    return render_template("inventory.html", products=rows, q=q)


@app.route("/products/add", methods=["GET", "POST"])
def product_add():
    redir = _require_login()
    if redir:
        return redir
    if request.method == "POST":
        sku = (request.form.get("sku") or "").strip()
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        note = (request.form.get("note") or "").strip()
        qty_raw = (request.form.get("quantity") or "").strip()
        price_raw = (request.form.get("unit_price") or "").strip()
        err = _validate_product_fields(sku, name, qty_raw, price_raw)
        if err:
            flash(err, "error")
            return render_template("product_form.html", mode="add", form=request.form), 400
        quantity = int(qty_raw)
        unit_price = float(price_raw)
        conn = db_conn()
        try:
            conn.execute(
                """
                INSERT INTO products (sku, name, category, quantity, unit_price, note, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (sku, name, category, quantity, unit_price, note, _now_iso(), _now_iso()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("商品编号（SKU）已存在，请更换。", "error")
            return render_template("product_form.html", mode="add", form=request.form), 409
        flash("添加成功。", "success")
        return redirect(url_for("inventory"))
    return render_template("product_form.html", mode="add", form={})


@app.route("/products/<int:pid>/edit", methods=["GET", "POST"])
def product_edit(pid: int):
    redir = _require_login()
    if redir:
        return redir
    conn = db_conn()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    if not row:
        flash("记录不存在。", "error")
        return redirect(url_for("inventory")), 404
    if request.method == "POST":
        sku = (request.form.get("sku") or "").strip()
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        note = (request.form.get("note") or "").strip()
        qty_raw = (request.form.get("quantity") or "").strip()
        price_raw = (request.form.get("unit_price") or "").strip()
        err = _validate_product_fields(sku, name, qty_raw, price_raw)
        if err:
            flash(err, "error")
            return render_template(
                "product_form.html", mode="edit", product_id=pid, form=request.form
            ), 400
        quantity = int(qty_raw)
        unit_price = float(price_raw)
        try:
            conn.execute(
                """
                UPDATE products SET sku=?, name=?, category=?, quantity=?, unit_price=?, note=?, updated_at=?
                WHERE id=?
                """,
                (sku, name, category, quantity, unit_price, note, _now_iso(), pid),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("商品编号（SKU）与其他记录冲突。", "error")
            return render_template(
                "product_form.html", mode="edit", product_id=pid, form=request.form
            ), 409
        flash("修改成功。", "success")
        return redirect(url_for("inventory"))
    form = dict(row)
    return render_template("product_form.html", mode="edit", product_id=pid, form=form)


@app.route("/products/<int:pid>/delete", methods=["POST"])
def product_delete(pid: int):
    redir = _require_login()
    if redir:
        return redir
    conn = db_conn()
    conn.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    flash("已删除。", "success")
    return redirect(url_for("inventory"))


def _validate_product_fields(sku: str, name: str, qty_raw: str, price_raw: str) -> str | None:
    if not sku:
        return "商品编号不能为空。"
    if not name:
        return "商品名称不能为空。"
    if not re.fullmatch(r"[A-Za-z0-9._\-]{1,64}", sku):
        return "商品编号仅允许字母、数字及 ._- ，长度不超过 64。"
    if not qty_raw.isdigit():
        return "库存数量必须为非负整数。"
    if int(qty_raw) < 0:
        return "库存数量必须为非负整数。"
    try:
        price = float(price_raw)
    except ValueError:
        return "单价格式不正确。"
    if price < 0:
        return "单价不能为负数。"
    return None


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("数据库已初始化：", __import__("db").get_db_path())


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
