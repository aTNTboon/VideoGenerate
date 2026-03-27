from pathlib import Path

from MyCode.core.services.video_creation_service import (
    DirectSubtitleRequest,
    PlainTextSubtitleProvider,
    VideoCreationService,
)


class FakeEditor:
    def __init__(self):
        self.called = None

    def add_subtitles(self, video_path, subtitle_path, output_path):
        self.called = (video_path, subtitle_path, output_path)
        Path(output_path).write_text("ok", encoding="utf-8")
        return output_path


def test_video_creation_service_accepts_text_subtitle(tmp_path):
    provider = PlainTextSubtitleProvider(base_dir=str(tmp_path / "sub"))
    editor = FakeEditor()
    service = VideoCreationService(provider, editor)

    video = tmp_path / "in.mp4"
    video.write_text("dummy", encoding="utf-8")
    output = tmp_path / "out.mp4"

    result = service.add_subtitle_to_direct_video(
        DirectSubtitleRequest(
            video_path=str(video), subtitle_text="hello", output_path=str(output)
        )
    )

    assert result == str(output)
    assert editor.called is not None
    assert Path(editor.called[1]).exists()


def test_subtitle_provider_requires_text_or_path(tmp_path):
    provider = PlainTextSubtitleProvider(base_dir=str(tmp_path))
    try:
        provider.ensure_subtitle_file(None, None)
        assert False, "expected ValueError"
    except ValueError:
        assert True
