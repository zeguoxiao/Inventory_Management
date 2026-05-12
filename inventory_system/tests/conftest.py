import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def client(tmp_path, monkeypatch):
    import db as db_mod

    monkeypatch.setattr(db_mod, "get_db_path", lambda: tmp_path / "test_inventory.db")

    # 确保 app 在 monkeypatch 之后加载
    sys.modules.pop("app", None)
    import app as app_mod

    db_mod.init_db()
    app_mod.app.config.update(TESTING=True)
    return app_mod.app.test_client()
