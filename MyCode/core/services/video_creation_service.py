import os
import shutil
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

import MyCode.util.Video_Edit_Util.VideoComposer as VideoComposer
from MyCode.core.library.result_paths import ResultPathManager


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
    def __init__(self):
        self.base_dir = ResultPathManager.subdir("subtitle")

    def ensure_subtitle_file(self, subtitle_text: str | None, subtitle_path: str | None) -> str:
        if subtitle_path:
            return subtitle_path
        if not subtitle_text:
            raise ValueError("必须提供 subtitle_text 或 subtitle_path")

        sid = uuid.uuid4().hex
        path = self.base_dir / f"direct_{sid}.srt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(subtitle_text)
        return ResultPathManager.to_relative(str(path))


class MoviePyVideoEditor(IVideoEditor):
    def add_subtitles(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        video_abs = ResultPathManager.to_absolute(video_path)
        subtitle_abs = ResultPathManager.to_absolute(subtitle_path)
        output_abs = ResultPathManager.to_absolute(output_path)
        VideoComposer.add_subtitles(video_abs, subtitle_abs, output_abs)
        return ResultPathManager.to_relative(output_abs)


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
            output_path = str(ResultPathManager.subdir("video") / f"direct_{uuid.uuid4().hex}.mp4")
            output_path = ResultPathManager.to_relative(output_path)
        return self.video_editor.add_subtitles(request.video_path, subtitle_file, output_path)


def persist_uploaded_video(file_storage) -> str:
    base_dir = ResultPathManager.subdir("uploads")
    ext = os.path.splitext(file_storage.filename or "upload.mp4")[1] or ".mp4"
    filename = f"upload_{uuid.uuid4().hex}{ext}"
    path = base_dir / filename
    file_storage.save(str(path))
    return ResultPathManager.to_relative(str(path))


def persist_uploaded_subtitle(file_storage) -> str:
    base_dir = ResultPathManager.subdir("subtitle")
    ext = os.path.splitext(file_storage.filename or "subtitle.srt")[1] or ".srt"
    filename = f"subtitle_{uuid.uuid4().hex}{ext}"
    path = base_dir / filename
    file_storage.save(str(path))
    return ResultPathManager.to_relative(str(path))


def copy_video_to_workspace(src_path: str) -> str:
    src_abs = ResultPathManager.to_absolute(src_path)
    if not os.path.exists(src_abs):
        raise FileNotFoundError(f"视频文件不存在: {src_path}")
    base_dir = ResultPathManager.subdir("uploads")
    ext = os.path.splitext(src_abs)[1] or ".mp4"
    dst_path = base_dir / f"local_{uuid.uuid4().hex}{ext}"
    shutil.copy2(src_abs, dst_path)
    return ResultPathManager.to_relative(str(dst_path))
