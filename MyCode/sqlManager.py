import importlib.util
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional

if importlib.util.find_spec("pymysql") is not None:
    import pymysql
    from pymysql.cursors import DictCursor
else:
    pymysql = None
    DictCursor = None


class VideoDBManager:
    """Database manager with MySQL-first strategy and local SQLite fallback.

    Notes:
    - Preferred backend: MySQL (compatible with current deployment).
    - Fallback backend: local SQLite file (used as local H2-style embedded DB).
    - For fallback mode, tables are auto-created on initialization.
    """

    def __init__(
        self,
        host: str = "localhost",
        user: str = "algernon",
        password: str = "123",
        db: str = "video_db",
        port: int = 3306,
        sqlite_path: Optional[str] = None,
    ):
        self.db_name = db
        self.backend = "mysql"
        self.sqlite_path = sqlite_path or os.path.join(
            os.path.dirname(__file__), "data", f"{db}.sqlite3"
        )

        try:
            if pymysql is None:
                raise RuntimeError("pymysql not installed")
            self.conn: Any = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=db,
                port=port,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        except Exception:
            os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
            self.backend = "sqlite"
            self.conn = sqlite3.connect(self.sqlite_path)
            self.conn.row_factory = sqlite3.Row
            self._initialize_sqlite_schema()

    @property
    def is_sqlite(self) -> bool:
        return self.backend == "sqlite"

    @contextmanager
    def _cursor(self):
        if self.is_sqlite:
            cursor = self.conn.cursor()
        else:
            cursor = self.conn.cursor(DictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

    def _execute(self, sql: str, params: Iterable[Any] = ()) -> Dict[str, Any]:
        sql = self._adapt_sql(sql)
        with self._cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return {
                "rowcount": cursor.rowcount,
                "lastrowid": getattr(cursor, "lastrowid", None),
            }

    def _query_all(self, sql: str, params: Iterable[Any] = ()) -> List[Dict[str, Any]]:
        sql = self._adapt_sql(sql)
        with self._cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
        return self._normalize_rows(rows)

    def _query_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[Dict[str, Any]]:
        sql = self._adapt_sql(sql)
        with self._cursor() as cursor:
            cursor.execute(sql, tuple(params))
            row = cursor.fetchone()
        if row is None:
            return None
        return self._normalize_row(row)

    def _adapt_sql(self, sql: str) -> str:
        if not self.is_sqlite:
            return sql
        return sql.replace("%s", "?")

    def _normalize_rows(self, rows: Any) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for row in rows:
            normalized.append(self._normalize_row(row))
        return normalized

    def _normalize_row(self, row: Any) -> Dict[str, Any]:
        if isinstance(row, sqlite3.Row):
            return {k: row[k] for k in row.keys()}
        return dict(row)

    def _initialize_sqlite_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT,
                    uid INTEGER,
                    theme INTEGER DEFAULT 0,
                    scene TEXT,
                    src_path TEXT,
                    audio_path TEXT,
                    mood INTEGER DEFAULT 0,
                    music_path TEXT DEFAULT '',
                    video_path TEXT DEFAULT '',
                    output_path TEXT DEFAULT '',
                    step INTEGER DEFAULT 0,
                    prompts TEXT DEFAULT '',
                    text TEXT DEFAULT '默认小说名'
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS finishedVideo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT,
                    text TEXT,
                    mood TEXT,
                    videoPath TEXT
                )
                """
            )

    # 插入视频片段信息
    def insert_video(self, data: Dict):
        sql = """INSERT INTO videos
        (video_id, uid, theme, scene, src_path, audio_path, mood, music_path, video_path, output_path, step,prompts,text)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self._execute(
            sql,
            (
                data.get("video_id"),
                data.get("uid"),
                int(data.get("theme", 0)),
                data.get("scene"),
                data.get("src_path"),
                data.get("audio_path"),
                int(data.get("mood", 0)),
                data.get("music_path", ""),
                data.get("video_path", ""),
                data.get("output_path", ""),
                data.get("step", 0),
                data.get("prompts", ""),
                data.get("text", "默认小说名"),
            ),
        )
        self.conn.commit()

    def query_videos(self, filters: Dict):
        conditions = []
        params = []

        if filters.get("video_id"):
            conditions.append("video_id = %s")
            params.append(filters["video_id"])
        if filters.get("theme") is not None:
            conditions.append("theme = %s")
            params.append(filters["theme"])
        if filters.get("mood") is not None:
            conditions.append("mood = %s")
            params.append(filters["mood"])
        if filters.get("step") is not None:
            conditions.append("step = %s")
            params.append(filters["step"])
        if filters.get("name"):
            conditions.append("text LIKE %s")
            params.append(f"%{filters['name']}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"SELECT * FROM videos {where_clause} ORDER BY id DESC"
        return self._query_all(sql, params)

    def update_step(self, id: int, step: int):
        self._execute("UPDATE videos SET step=%s WHERE id=%s", (step, id))
        self.conn.commit()

    def update_output_path(self, id: int, output_path: str):
        self._execute("UPDATE videos SET output_path=%s WHERE id=%s", (output_path, id))
        self.conn.commit()

    def update_field(self, id: int, field: str, value):
        if field not in {
            "step",
            "output_path",
            "video_path",
            "audio_path",
            "src_path",
            "mood",
            "theme",
            "prompts",
            "music_path",
        }:
            raise ValueError(f"更新字段 {field} 不在允许列表内")

        sql = f"UPDATE videos SET {field}=%s WHERE id=%s"
        self._execute(sql, (value, id))
        self.conn.commit()

    def get_pending_videos(self, step: int) -> List[Dict]:
        return self._query_all("SELECT * FROM videos WHERE step = %s", (step,))

    def upsert_video_field(self, id: int, uid: int, field: str, value):
        allowed_fields = {
            "step",
            "output_path",
            "video_path",
            "audio_path",
            "src_path",
            "mood",
            "theme",
            "music_path",
            "prompts",
        }
        if field not in allowed_fields:
            raise ValueError(f"字段 {field} 不允许更新")

        if self.is_sqlite:
            existing = self._query_one("SELECT id FROM videos WHERE id = %s", (id,))
            if existing:
                self._execute(f"UPDATE videos SET {field}=%s WHERE id=%s", (value, id))
            else:
                self._execute(
                    f"INSERT INTO videos (id, uid, {field}) VALUES (%s, %s, %s)",
                    (id, uid, value),
                )
        else:
            sql = f"""
            INSERT INTO videos (id, uid, {field})
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE {field} = VALUES({field})
            """
            self._execute(sql, (id, uid, value))
        self.conn.commit()

    def selectAll(self):
        sql = """
        SELECT *
        FROM videos t
        WHERE t.video_id IN (
            SELECT video_id
            FROM videos
            GROUP BY video_id
            HAVING MIN(step) = 4 AND MAX(step) = 4
        )
        ORDER BY uid;
        """
        return self._query_all(sql)

    def selectByText(self, text: str):
        sql = """
        SELECT *
        FROM videos
        WHERE text LIKE %s
        ORDER BY uid;
        """
        return self._query_all(sql, (f"%{text}%",))

    def get_completion_ratio(self, text: str) -> float:
        sql = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN step = 5 THEN 1 ELSE 0 END) AS completed
        FROM videos
        WHERE text LIKE %s;
        """
        row = self._query_one(sql, (f"%{text}%",)) or {}

        total = row.get("total") or 0
        completed = row.get("completed") or 0
        if total == 0:
            return 0.0
        return completed / total

    def delete_from_id(self, id: int, table: str):
        if table not in {"videos", "finishedVideo"}:
            raise ValueError("非法表名")
        self._execute(f"DELETE FROM {table} WHERE id = %s", (id,))
        self.conn.commit()

    def insert_finished_video(self, video_id, text, mood, videoPath):
        sql = """
            INSERT INTO finishedVideo (video_id, text, mood, videoPath)
            VALUES (%s, %s, %s, %s)
        """
        result = self._execute(sql, (video_id, text, mood, videoPath))
        self.conn.commit()
        return result.get("lastrowid")

    def delete_finished_video(self, id):
        result = self._execute("DELETE FROM finishedVideo WHERE id = %s", (id,))
        self.conn.commit()
        return result.get("rowcount", 0)

    def update_finished_video(
        self, id, video_id=None, text=None, mood=None, videoPath=None
    ):
        updates = []
        params = []
        if video_id is not None:
            updates.append("video_id = %s")
            params.append(video_id)
        if text is not None:
            updates.append("text = %s")
            params.append(text)
        if mood is not None:
            updates.append("mood = %s")
            params.append(mood)
        if videoPath is not None:
            updates.append("videoPath = %s")
            params.append(videoPath)

        if not updates:
            return 0

        sql = f"UPDATE finishedVideo SET {', '.join(updates)} WHERE id = %s"
        params.append(id)
        result = self._execute(sql, params)
        self.conn.commit()
        return result.get("rowcount", 0)

    def query_finished_videos(
        self,
        id=None,
        video_id=None,
        text=None,
        mood=None,
        videoPath=None,
        order_by="id DESC",
    ):
        conditions = []
        params = []

        if id is not None:
            conditions.append("id = %s")
            params.append(id)
        if video_id is not None:
            conditions.append("video_id = %s")
            params.append(video_id)
        if text is not None:
            conditions.append("text = %s")
            params.append(text)
        if mood is not None:
            conditions.append("mood = %s")
            params.append(mood)
        if videoPath is not None:
            conditions.append("videoPath = %s")
            params.append(videoPath)

        base_sql = "SELECT id, video_id, text, mood, videoPath FROM finishedVideo"
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)

        allowed_order = {"id DESC", "id ASC", "video_id DESC", "video_id ASC", None}
        if order_by not in allowed_order:
            order_by = "id DESC"
        if order_by:
            base_sql += f" ORDER BY {order_by}"

        return self._query_all(base_sql, params)
