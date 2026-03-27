import io

from MyCode import Controller


class FakeCreationService:
    def add_subtitle_to_direct_video(self, request_dto):
        assert request_dto.video_path
        return "/tmp/subbed.mp4"


def test_add_subtitle_endpoint_accepts_uploaded_video(monkeypatch):
    Controller.app.config["TESTING"] = True
    monkeypatch.setattr(Controller, "creation_service", FakeCreationService())
    monkeypatch.setattr(Controller, "persist_uploaded_video", lambda f: "/tmp/input.mp4")

    client = Controller.app.test_client()
    response = client.post(
        "/video/addSubtitle",
        data={
            "video": (io.BytesIO(b"video"), "a.mp4"),
            "subtitle_text": "hello",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["code"] == 200
    assert json_data["data"]["videoPath"] == "/tmp/subbed.mp4"


def test_add_subtitle_endpoint_requires_video_source():
    Controller.app.config["TESTING"] = True
    client = Controller.app.test_client()
    response = client.post("/video/addSubtitle", data={"subtitle_text": "hello"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["code"] == 400
