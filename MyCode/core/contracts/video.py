from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IVideoRepository(ABC):
    @abstractmethod
    def get_pending_videos(self, step: int) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def query_videos(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def select_by_text(self, text: str) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def delete_video_by_id(self, record_id: int) -> None: ...

    @abstractmethod
    def insert_finished_video(self, video_id, text, mood, video_path) -> int: ...

    @abstractmethod
    def query_finished_videos(self, **filters) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def update_finished_video(self, fid: int, **payload) -> int: ...

    @abstractmethod
    def delete_finished_video(self, fid: int) -> int: ...


class IVideoQueryService(ABC):
    @abstractmethod
    def get_videos_by_step(self, step: int) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def query_videos(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def query_videos_by_name(self, name: str) -> List[Dict[str, Any]]: ...
