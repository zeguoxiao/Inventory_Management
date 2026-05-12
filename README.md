# 简易商品库存管理系统（5G 软件工程实训）

## 功能概要

- 用户注册 / 登录 / 退出（密码哈希存储）
- 商品信息增删改查；支持关键词模糊查询（编号、名称、类别、备注）
- 数据持久化：SQLite（`data/inventory.db`，重启数据保留）

## 运行环境

- Python 3.10+
- 依赖见 `requirements.txt`

## 本地运行    
(*****直接打开inventory_system文件夹下的网站启动.bat也可以*****)

```powershell
cd inventory_system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app init-db
python app.py
```

浏览器访问：<http://127.0.0.1:5000>

首次使用请先「注册」账号，再登录维护库存。

## 测试

```powershell
pytest -q
```

## 目录说明

| 路径 | 说明 |
|------|------|
| `app.py` | Web 应用入口与路由 |
| `db.py` | 数据库连接与初始化 |
| `schema.sql` | 表结构（可与 `flask init-db` 对照） |
| `templates/` | 页面模板 |
| `static/` | 样式 |
| `data/` | 运行时自动生成 SQLite 文件 |

## 作业文档

上级目录或本目录生成的 `软件工程实训_简易商品库存管理系统_文档.docx` 含需求、设计、测试与报告纲要，请按任课教师要求补充截图、签名与封面。
