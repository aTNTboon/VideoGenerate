import pymysql
from typing import List, Dict
from pymysql.cursors import DictCursor


class VideoDBManager:
    def __init__(
        self,
        host="localhost",
        user="algernon",
        password="123",
        db="video_db",
        port=3306,
    ):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    # 插入视频片段信息
    def insert_video(self, data: Dict):
        sql = """INSERT INTO videos 
        (video_id, uid, theme, scene, src_path, audio_path, mood, music_path, video_path, output_path, step,prompts,text)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
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

    # 更新 step

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

        # 🔥 模糊查询
        if filters.get("name"):
            conditions.append("text LIKE %s")
            params.append(f"%{filters['name']}%")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"SELECT * FROM videos {where_clause} ORDER BY id DESC"

        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, tuple(params))
            result = cursor.fetchall()

        return result

    def update_step(self, id: int, step: int):
        sql = "UPDATE videos SET step=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (step, id))
        self.conn.commit()

    # 更新 output_path
    def update_output_path(self, id: int, output_path: str):
        sql = "UPDATE videos SET output_path=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (output_path, id))
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
        }:
            raise ValueError(f"更新字段 {field} 不在允许列表内")

        sql = f"UPDATE videos SET {field}=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (value, id))
        self.conn.commit()

    # 查询未完成的视频（step < 3）
    def get_pending_videos(self, step: int) -> List[Dict]:
        sql = "SELECT * FROM videos WHERE step = %s"
        with self.conn.cursor(DictCursor) as cursor:  # dictionary=True 返回字典
            cursor.execute(sql, (step,))
            result = cursor.fetchall()
            return list(result)

    def upsert_video_field(self, id: int, uid: int, field: str, value):
        """
        如果记录存在就更新字段，否则插入一条新记录。

        :param video_id: 视频 ID
        :param uid: 视频片段 ID
        :param field: 要更新的字段名
        :param value: 字段值
        """
        # 允许更新的字段列表，避免注入
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

        sql = f"""
        INSERT INTO videos (id, uid, {field})
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE {field} = VALUES({field})
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (id, uid, value))
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
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()  # 获取所有查询结果
        return result

    def selectByText(self, text: str):
        sql = """
        SELECT *
        FROM videos
        WHERE text LIKE %s
        ORDER BY uid;
        """
        param = (f"%{text}%",)

        with self.conn.cursor() as cursor:
            cursor.execute(sql, param)
            result = cursor.fetchall()

        return result

    def get_completion_ratio(self, text: str) -> float:
        """
        返回指定小说 text 的完成度（step=5占比），step=5视为完成
        """
        sql = """
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN step = 5 THEN 1 ELSE 0 END) AS completed
        FROM videos
        WHERE text LIKE %s;
        """
        param = (f"%{text}%",)

        with self.conn.cursor() as cursor:
            cursor.execute(sql, param)
            row = cursor.fetchone()

        total = row["total"] or 0  # type: ignore
        completed = row["completed"] or 0  # type: ignore

        if total == 0:
            return 0.0

        return completed / total

    def delete_from_id(self, id: int, table: str):

        sql = "DELETE FROM {} WHERE id = %s".format(table)

        with self.conn.cursor() as cursor:
            cursor.execute(sql, (id,))

        self.conn.commit()

    def insert_finished_video(self, video_id, text, mood, videoPath):
        sql = """
            INSERT INTO finishedVideo (video_id, text, mood, videoPath)
            VALUES (%s, %s, %s, %s)
        """
        conn = self.conn

        with conn.cursor() as cursor:
            cursor.execute(sql, (video_id, text, mood, videoPath))
        conn.commit()
        return cursor.lastrowid

    def delete_finished_video(self, id):
        """根据主键删除记录"""
        sql = "DELETE FROM finishedVideo WHERE id = %s"
        conn = self.conn

        with conn.cursor() as cursor:
            cursor.execute(sql, (id,))
        conn.commit()
        return cursor.rowcount

    def update_finished_video(
        self, id, video_id=None, text=None, mood=None, videoPath=None
    ):
        """根据主键更新记录（仅更新传入的非 None 字段）"""
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

        conn = self.conn
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount

    def query_finished_videos(
        self,
        id=None,
        video_id=None,
        text=None,
        mood=None,
        videoPath=None,
        order_by="id DESC",
    ):
        """
        根据传入的条件查询记录，支持多个字段组合（AND 关系）。
        参数说明：
            id, video_id, text, mood, videoPath: 查询条件（等值匹配）
            order_by: 排序字段及方向，例如 "id DESC", "video_id ASC"；若无需排序可传入 None
        返回：符合条件的记录列表（字典格式）
        """
        conditions = []
        params = []

        if id is not None:
            conditions.append("id = %s")
            params.append(id)
        if video_id is not None:
            conditions.append("video_id = %s")
            params.append(video_id)
        if text is not None:
            # 若需要模糊查询可将 '=' 改为 'LIKE' 并拼接 %text%
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

        if order_by:
            base_sql += f" ORDER BY {order_by}"

        conn = self.conn
        with conn.cursor() as cursor:
            cursor.execute(base_sql, params)
            return cursor.fetchall()
