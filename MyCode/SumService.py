
from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow
from MyCode.util.Subtitle_Util.Whisper_Sybtitle import Whisper_Sybtitle_Util
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.util.self_requestUtil.RequestAI import RequestAI
from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.SceneParser import self_parse


class SumService:
    def __init__(self,requestUtil:Base_Request,TTSUtil:Base_Audio_Util,SubtitleUtil:Base_Subtitle_Util,Image_Generate_Util:Base_Image_Generate_Util):
        self.RU=requestUtil
        self.TTS=TTSUtil
        self.SU=SubtitleUtil
        self.IGU=Image_Generate_Util
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
            self.SU.generate_src(videoName)
            
            uid+=1
        
        self.Video_id+=1



if __name__ == '__main__':
    SumService(
        RequestAI(),
        Edge_TTS_Util(),              # ✅ 实例
        Whisper_Sybtitle_Util(),
        Local_Image_WorkFlow("")
    )


