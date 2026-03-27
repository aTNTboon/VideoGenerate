from typing import Any, Dict, List

from MyCode.sqlManager import VideoDBManager
from MyCode.video_contracts import IVideoRepository


class SqlVideoRepository(IVideoRepository):
    def __init__(self, db: VideoDBManager):
        self.db = db

    def get_pending_videos(self, step: int) -> List[Dict[str, Any]]:
        return self.db.get_pending_videos(step)

    def query_videos(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.db.query_videos(filters)

    def select_by_text(self, text: str) -> List[Dict[str, Any]]:
        return self.db.selectByText(text)

    def delete_video_by_id(self, record_id: int) -> None:
        self.db.delete_from_id(record_id, "videos")

    def insert_finished_video(self, video_id, text, mood, video_path) -> int:
        return self.db.insert_finished_video(video_id, text, mood, video_path)

    def query_finished_videos(self, **filters) -> List[Dict[str, Any]]:
        return self.db.query_finished_videos(**filters)

    def update_finished_video(self, fid: int, **payload) -> int:
        return self.db.update_finished_video(fid, **payload)

    def delete_finished_video(self, fid: int) -> int:
        return self.db.delete_finished_video(fid)
