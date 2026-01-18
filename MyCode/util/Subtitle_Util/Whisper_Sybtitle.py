import whisper
import re
from whisper.utils import get_writer
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.Setting import Setting


import numpy as np

def npfloat16_to_srt_time(seconds: np.float16) -> str:
    """
    将 np.float16 秒数转为 SRT 时间格式 HH:MM:SS,mmm
    """
    # 转为 Python float 以保证计算精度
    sec = float(seconds)

    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    secs = int(sec % 60)
    millis = int(round((sec - int(sec)) * 1000))

    # 处理可能的 1000 毫秒进位
    if millis >= 1000:
        millis -= 1000
        secs += 1
    if secs >= 60:
        secs -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        hours += 1

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

class Whisper_Sybtitle_Util(Base_Subtitle_Util):
    def __init__(self):
        super().__init__()
        self.model = whisper.load_model(Setting.SUBTITLE_MODEL)

    def generate_src(self, videoName: str, content: str):
        prefix = [
            '。', '！', '？', '；', '，', '——', '…', '“', '”', '‘', '’','”','“',
            '（', '）', '【', '】', '《', '》',' ','、',
            '.', ',', ';', ':', '!', '?', '"', "'", '(', ')', '[', ']', '{', '}', '<', '>', '-', '–', '—', '…',' '
        ]

        pattern = "[" + re.escape("".join(prefix)) + "]"

        content_no_punct = re.sub(pattern, '', content)
        # ========== 步骤2：获取词级时间戳 ==========
        result = self.model.transcribe(
            audio=f"/article/audio/{videoName}.wav",
            language=Setting.src_language,
            initial_prompt="",
            task="transcribe",
            verbose=False,
            word_timestamps=True,
            fp16=False,
            temperature=0.0,
            best_of=1,
            condition_on_previous_text=False,
        )
        content_index=0
        with open(f'/article/subtitle/{videoName}.srt', 'w') as w:
            
            index=1

            segments = result["segments"]
            for segment in segments:
                w.write(f"{index}\n")
                start:np.float16 = segment["start"]
                end:np.float16 = segment["end"]
                w.write(f"{npfloat16_to_srt_time(start)} --> {npfloat16_to_srt_time(end)}\n")
                text:str = segment["text"].strip()
                text_chars = list(text)  # 转成列表
                for i in range(len(text_chars)):
                    if text_chars[i] not in prefix:
                        text_chars[i] = content_no_punct[content_index]
                        content_index += 1  # 替换后索引向后移动

                        if content_index >= len(content_no_punct):
                            break

                w.write("".join(text_chars))
                w.write("\n\n")
                index+=1

if __name__ == '__main__':
    wu = Whisper_Sybtitle_Util()
    wu.generate_src(
        "test",
        "2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋"
    )
