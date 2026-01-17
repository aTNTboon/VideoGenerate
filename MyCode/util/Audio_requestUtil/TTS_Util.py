import os
import asyncio
import edge_tts
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.Setting import Setting

class Edge_TTS_Util(Base_Audio_Util):
    def __init__(self):
        super().__init__()

    async def _audio_request_async(self, uid, story):
        # 确保目录存在
        os.makedirs("/article/audio", exist_ok=True)
        # 调用 edge-tts
        communicate = edge_tts.Communicate(story, Setting.VOICE)
        await communicate.save(f"/article/audio/{uid}.wav")

    def audio_request(self, uid, story):
        # 同步包装
        asyncio.run(self._audio_request_async(uid, story))


if __name__ == "__main__":
    Edge_TTS_Util().audio_request("test", "测试")
