# import whisper
# from whisper.utils import get_writer
# from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
# from MyCode.Setting import Setting

# #
# # 转写音频


# class Whisper_Sybtitle_Util(Base_Subtitle_Util):
#     def __init__(self):
#         super().__init__()
#         self.model = whisper.load_model(Setting.SUBTITLE_MODEL)

#     def generate_src(self, videoName:str,content:str):
#         result = self.model.transcribe(
#             audio=f"/article/audio/{videoName}.wav",
#             language=Setting.src_language,          # ✅ 指定识别语言：强制中文，杜绝识别成英文/其他语言【重中之重】
#             initial_prompt=content, # ✅ 你要的「关键字/核心内容」全写这里！！！
#             task="transcribe",           # ✅ 任务类型：转录字幕（固定值，不要改）
#             verbose=False,               # ✅ 关闭控制台冗余日志，整洁输出
#             word_timestamps=False,       # ✅ 关闭单词级时间戳，只生成句子级SRT字幕（适合你的场景）
#             fp16=Setting.fp16                   # ✅ 本地CPU运行必加！否则大概率报错，GPU运行可改True
#         )
#         # 获取 writer
#         writer = get_writer("srt", output_dir="/article/subtitle")  # output_dir="." 表示当前目录
#         # 调用 writer 生成字幕文件
#         writer(result, videoName)  # type: ignore 


# if __name__ == '__main__':
#     wu = Whisper_Sybtitle_Util()
#     wu.generate_src("test",
#                     "2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋")