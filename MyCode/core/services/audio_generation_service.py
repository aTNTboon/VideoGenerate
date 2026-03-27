from typing import Any

from MyCode.core.contracts.audio import IAudioGenerationService, IAudioProvider


class EdgeTTSProvider(IAudioProvider):
    def __init__(self, engine: Any | None = None):
        if engine is None:
            from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util

            engine = Edge_TTS_Util()
        self.engine = engine

    def generate(self, uid: str, content: str) -> str:
        return self.engine.audio_request(uid, content)


class AudioGenerationService(IAudioGenerationService):
    def __init__(self, provider: IAudioProvider):
        self.provider = provider

    def create_voice(self, uid: str, content: str) -> str:
        return self.provider.generate(uid, content)
