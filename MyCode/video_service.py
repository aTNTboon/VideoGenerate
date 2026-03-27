from typing import Any, Dict, List

from MyCode.entity.VideoEntity import VideoEntity
from MyCode.video_contracts import IVideoQueryService, IVideoRepository


class VideoQueryService(IVideoQueryService):
    def __init__(self, repo: IVideoRepository):
        self.repo = repo

    @staticmethod
    def _to_entity_dict_list(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        video_list: List[VideoEntity] = []
        for video_dict in data:
            video = VideoEntity()
            video.id = str(video_dict.get("id", "0"))
            video.video_id = str(video_dict.get("video_id", ""))
            video.uid = str(video_dict.get("uid", ""))
            video.theme = int(video_dict.get("theme", 0))
            video.scene = str(video_dict.get("scene", ""))
            video.src_path = str(video_dict.get("src_path", ""))
            video.audio_path = str(video_dict.get("audio_path", ""))
            video.mood = int(video_dict.get("mood", 0))
            video.music_path = str(video_dict.get("music_path", ""))
            video.video_path = str(video_dict.get("video_path", ""))
            video.output_path = str(video_dict.get("output_path", ""))
            video.step = int(video_dict.get("step", 0))
            video.prompts = str(video_dict.get("prompts", ""))
            video.text = str(video_dict.get("text", "默认小说名"))
            video_list.append(video)
        return [item.to_dict() for item in video_list]

    def get_videos_by_step(self, step: int) -> List[Dict[str, Any]]:
        rows = self.repo.get_pending_videos(step)
        return self._to_entity_dict_list(rows)

    def query_videos(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows = self.repo.query_videos(filters)
        return self._to_entity_dict_list(rows)

    def query_videos_by_name(self, name: str) -> List[Dict[str, Any]]:
        rows = self.repo.select_by_text(name)
        return self._to_entity_dict_list(rows)
