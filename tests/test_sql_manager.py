import types

import pytest

from MyCode import sqlManager
from MyCode.sqlManager import VideoDBManager


@pytest.fixture
def force_mysql_fail(monkeypatch):
    fake = types.SimpleNamespace()

    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    fake.connect = _raise
    monkeypatch.setattr(sqlManager, "pymysql", fake)


def test_sqlite_fallback_initializes_schema(tmp_path, force_mysql_fail):
    db_file = tmp_path / "video.sqlite3"
    manager = VideoDBManager(db="unit_db", sqlite_path=str(db_file))

    assert manager.backend == "sqlite"
    assert db_file.exists()

    manager.insert_video(
        {
            "video_id": "v1",
            "uid": 1,
            "theme": 0,
            "scene": "scene",
            "src_path": "a.srt",
            "audio_path": "a.wav",
            "mood": 0,
            "step": 1,
        }
    )
    rows = manager.get_pending_videos(1)
    assert len(rows) == 1
    assert rows[0]["video_id"] == "v1"
