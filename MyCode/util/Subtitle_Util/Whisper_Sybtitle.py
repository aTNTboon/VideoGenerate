import whisper
from whisper.utils import get_writer
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.Setting import Setting

#
# 转写音频


class Whisper_Sybtitle_Util(Base_Subtitle_Util):
    def __init__(self):
        super().__init__()
        self.model = whisper.load_model(Setting.SUBTITLE_MODEL)

    def generate_src(self, uid):
        result = self.model.transcribe(f"/article/audio/{uid}.wav")

        # 获取 writer
        writer = get_writer("srt", output_dir="/article/subtitle")  # output_dir="." 表示当前目录

        # 调用 writer 生成字幕文件
        writer(result, "uid")  # type: ignore 
