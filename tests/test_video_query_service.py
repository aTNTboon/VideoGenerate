from MyCode.core.services.video_query_service import VideoQueryService


class FakeRepo:
    def get_pending_videos(self, step):
        return [
            {
                "id": 1,
                "video_id": "v1",
                "uid": 2,
                "theme": 3,
                "scene": "scene",
                "src_path": "a.srt",
                "audio_path": "a.wav",
                "mood": 1,
                "music_path": "",
                "video_path": "x.mp4",
                "output_path": "y.mp4",
                "step": step,
                "prompts": "p",
                "text": "name",
            }
        ]

    def query_videos(self, filters):
        return self.get_pending_videos(filters.get("step", 0))

    def select_by_text(self, text):
        rows = self.get_pending_videos(1)
        rows[0]["text"] = text
        return rows


def test_get_videos_by_step_maps_entity_dict():
    service = VideoQueryService(FakeRepo())
    rows = service.get_videos_by_step(7)
    assert rows[0]["step"] == 7
    assert rows[0]["video_id"] == "v1"


def test_query_videos_by_name_returns_mapped_text():
    service = VideoQueryService(FakeRepo())
    rows = service.query_videos_by_name("小说")
    assert rows[0]["text"] == "小说"
