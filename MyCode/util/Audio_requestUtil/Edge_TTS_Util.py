import os
import asyncio
import edge_tts
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.Setting import Setting
from MyCode.core.library.result_paths import ResultPathManager


class Edge_TTS_Util(Base_Audio_Util):
    def __init__(self):
        super().__init__()

    def close(self):
        return

    async def _audio_request_async(self, uid, story):
        """核心异步生成音频逻辑，出错等待20秒后重试"""
        # 确保目录存在
        audio_dir = ResultPathManager.subdir("audio")
        path: str = str(audio_dir / f"{uid}.wav")

        # 核心：出错后等待20秒重试，直到成功
        while True:
            try:
                # 原有调用逻辑完全保留
                communicate = edge_tts.Communicate(
                    story,
                    Setting.VOICE,
                    pitch=Setting.PITCH,
                    rate=Setting.RATE,
                    volume="+100%",
                )
                await communicate.save(path)
                return ResultPathManager.to_relative(path)  # 成功则返回路径，退出循环
            except Exception as e:
                # 捕获所有异常（包含503握手错误）
                print(f"音频生成失败：{str(e)}，将在20秒后重试...")
                await asyncio.sleep(20)  # 等待20秒后重新尝试

    def audio_request(self, uid, story) -> str:
        # 同步包装逻辑完全保留
        return asyncio.run(self._audio_request_async(uid, story))


if __name__ == "__main__":
    # 测试代码完全保留
    Edge_TTS_Util().audio_request(
        "test",
        "2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋。",
    )
