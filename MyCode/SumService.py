from MyCode.Setting import Setting
from MyCode.BaseService import BaseService
from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow
from MyCode.util.Subtitle_Util.Whisper_Sybtitle import Whisper_Sybtitle_Util
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.util.self_requestUtil.RequestAI import RequestAI
from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.SceneParser import self_parse
from MyCode.util.Image_Generate_Util.Base_Video_Generate_Util import Base_Video_Generate_Util
from enum import Enum


class StylizedModel(Enum):
    # 枚举成员：格式 成员名 = 值，值可以是 数字/字符串/对象 等任意类型
    GuFeng =  Local_Image_WorkFlow("")


class SumService(BaseService):
    def __init__(self,requestUtil:Base_Request,TTSUtil:Base_Audio_Util,SubtitleUtil:Base_Subtitle_Util):
        self.RU=requestUtil
        self.TTS=TTSUtil
        self.SU=SubtitleUtil
        self.Video_id=0
        self.UID2Video_Id: dict[int, list[str]] = {}
    def run(self):
        video_id=self.Video_id
        response= self.RU.request("")
        json_list = self_parse(response,video_id,0)
        uid=0
        self.UID2Video_Id[video_id]=[]
        for item in json_list:
            videoName=f"{video_id}_{uid}"
            self.UID2Video_Id[video_id].append(str(videoName))
            self.TTS.audio_request(videoName,item["text"])
            self.SU.generate_src(videoName,content)
            base: Base_Image_Generate_Util = StylizedModel[Setting.style[str(item['theme_id'])]].value
            video_Generator:Base_Video_Generate_Util = Base_Video_Generate_Util(base,self.RU)
            video_Generator.generateFrame(videoName,item["text"])
            uid+=1
        self.Video_id+=1



if __name__ == '__main__':
    RU=RequestAI()            
    videoName="0_0"

    base: Base_Image_Generate_Util = StylizedModel[Setting.style["1"]].value
    video_Generator:Base_Video_Generate_Util = Base_Video_Generate_Util(base,RU)
    video_Generator.generateFrame(videoName,"2022年的秋天，淅淅沥沥的小雨从灰色的天空落下，打湿了城市街道。胡同里，十七八岁的少年庆尘和一位老爷子坐在超市雨棚下对弈，雨棚之外一片灰暗，雨水把地面浸成浅黑色，雨棚下却留着一块干净的净土。棋盘上杀机毕露，少年平静地提醒老头“将军”，老头无奈认输。庆尘拿了20块钱，坐回棋盘旁复盘，两人之间形成了一种奇异的默契——庆尘教棋，老头输钱学棋。")


#
#Prompt ID: 1c043547-5ef7-44b9-b8e4-c187465b2722

