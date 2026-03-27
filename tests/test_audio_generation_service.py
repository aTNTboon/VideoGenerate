from MyCode.core.services.audio_generation_service import AudioGenerationService


class FakeAudioProvider:
    def __init__(self):
        self.last = None

    def generate(self, uid: str, content: str) -> str:
        self.last = (uid, content)
        return f"/tmp/{uid}.wav"


def test_audio_generation_service_delegates_to_provider():
    provider = FakeAudioProvider()
    service = AudioGenerationService(provider)

    path = service.create_voice("u1", "旁白")

    assert path == "/tmp/u1.wav"
    assert provider.last == ("u1", "旁白")
