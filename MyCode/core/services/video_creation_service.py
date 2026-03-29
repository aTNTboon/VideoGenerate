import os
import shutil
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

import MyCode.util.Video_Edit_Util.VideoComposer as VideoComposer


@dataclass
class DirectSubtitleRequest:
    video_path: str
    subtitle_text: str | None = None
    subtitle_path: str | None = None
    output_path: str | None = None


class ISubtitleProvider(ABC):
    @abstractmethod
    def ensure_subtitle_file(self, subtitle_text: str | None, subtitle_path: str | None) -> str:
        """Return a subtitle file path that can be consumed by video editor."""


class IVideoEditor(ABC):
    @abstractmethod
    def add_subtitles(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        """Attach subtitle to an existing video and return output path."""


class PlainTextSubtitleProvider(ISubtitleProvider):
    def __init__(self, base_dir: str = "/article/subtitle"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def ensure_subtitle_file(self, subtitle_text: str | None, subtitle_path: str | None) -> str:
        if subtitle_path:
            return subtitle_path
        if not subtitle_text:
            raise ValueError("必须提供 subtitle_text 或 subtitle_path")

        sid = uuid.uuid4().hex
        path = os.path.join(self.base_dir, f"direct_{sid}.srt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(subtitle_text)
        return path


class MoviePyVideoEditor(IVideoEditor):
    def add_subtitles(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        VideoComposer.add_subtitles(video_path, subtitle_path, output_path)
        return output_path


class VideoCreationService:
    def __init__(self, subtitle_provider: ISubtitleProvider, video_editor: IVideoEditor):
        self.subtitle_provider = subtitle_provider
        self.video_editor = video_editor

    def add_subtitle_to_direct_video(self, request: DirectSubtitleRequest) -> str:
        subtitle_file = self.subtitle_provider.ensure_subtitle_file(
            request.subtitle_text, request.subtitle_path
        )
        output_path = request.output_path
        if not output_path:
            os.makedirs("/article/video/sub", exist_ok=True)
            output_path = f"/article/video/sub/direct_{uuid.uuid4().hex}.mp4"
        self.video_editor.add_subtitles(request.video_path, subtitle_file, output_path)
        return output_path


def persist_uploaded_video(file_storage, base_dir: str = "/article/video/uploads") -> str:
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(file_storage.filename or "upload.mp4")[1] or ".mp4"
    filename = f"upload_{uuid.uuid4().hex}{ext}"
    path = os.path.join(base_dir, filename)
    file_storage.save(path)
    return path


def persist_uploaded_subtitle(file_storage, base_dir: str = "/article/subtitle") -> str:
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(file_storage.filename or "subtitle.srt")[1] or ".srt"
    filename = f"subtitle_{uuid.uuid4().hex}{ext}"
    path = os.path.join(base_dir, filename)
    file_storage.save(path)
    return path


def copy_video_to_workspace(src_path: str, base_dir: str = "/article/video/uploads") -> str:
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"视频文件不存在: {src_path}")
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(src_path)[1] or ".mp4"
    dst_path = os.path.join(base_dir, f"local_{uuid.uuid4().hex}{ext}")
    shutil.copy2(src_path, dst_path)
    return dst_path
