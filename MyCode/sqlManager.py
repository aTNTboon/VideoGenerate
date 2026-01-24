import pymysql
from typing import List, Dict

class VideoDBManager:
    def __init__(self, host="localhost", user="algernon", password="123", db="video_db", port=3306):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    # 插入视频片段信息
    def insert_video(self, data: Dict):
        sql = """
        INSERT INTO videos 
        (video_id, uid, theme, scene, src_path, audio_path, mood, music_path, video_path, output_path, step)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (
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
                data.get("step", 0)
            ))
        self.conn.commit()

    # 更新 step
    def update_step(self, id: int, step: int):
        sql = "UPDATE videos SET step=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (step,id))
        self.conn.commit()

    # 更新 output_path
    def update_output_path(self, id: int, output_path: str):
        sql = "UPDATE videos SET output_path=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (output_path, id))
        self.conn.commit()
    def update_field(self, id: int, field: str, value):
        if field not in {"step", "output_path", "video_path", "audio_path", "src_path", "mood", "theme"}:
            raise ValueError(f"更新字段 {field} 不在允许列表内")
        
        sql = f"UPDATE videos SET {field}=%s WHERE id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (value, id))
        self.conn.commit()


    # 查询未完成的视频（step < 3）
    def get_pending_videos(self,step) -> List[Dict]:
        sql = "SELECT * FROM videos WHERE step=step"
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result =cursor.fetchall()
            return list(result)  

    def upsert_video_field(self, video_id: int, uid: int, field: str, value):
        """
        如果记录存在就更新字段，否则插入一条新记录。
        
        :param video_id: 视频 ID
        :param uid: 视频片段 ID
        :param field: 要更新的字段名
        :param value: 字段值
        """
        # 允许更新的字段列表，避免注入
        allowed_fields = {"step", "output_path", "video_path", "audio_path", "src_path", "mood", "theme", "music_path"}
        if field not in allowed_fields:
            raise ValueError(f"字段 {field} 不允许更新")

        sql = f"""
        INSERT INTO videos (video_id, uid, {field})
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE {field} = VALUES({field})
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (video_id, uid, value))
        self.conn.commit()

    def close(self):
        self.conn.close()
