# 简易商品库存管理系统（软件工程实训作业）

## 功能概要

- 用户注册 / 登录 / 退出（密码哈希存储）
- 商品信息增删改查；支持关键词模糊查询（编号、名称、类别、备注）
- 数据持久化：SQLite（`data/inventory.db`，重启数据保留）

## 运行环境

- Python 3.10+
- 依赖见 `requirements.txt`

## 本地运行    
😎下载到本地，直接打开inventory_system文件夹下的——网站启动.bat，也可以！！！

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




