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
    Edge_TTS_Util().audio_request("test", "2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋。")
