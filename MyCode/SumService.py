from datetime import date
import os
from MyCode.Setting import Setting
from MyCode.BaseService import BaseService
from MyCode.sqlManager import VideoDBManager
from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.util.Image_Generate_Util.Base_Direct_Generate_Util import Base_Direct_Generate_Util
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.Image_Generate_Util.Base_Video_Util import Base_Video_Util
from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow
from MyCode.util.Subtitle_Util.Whisper_Sybtitle import Whisper_Sybtitle_Util
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.util.self_requestUtil.RequestAI import RequestAI
from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.SceneParser import self_parse
from MyCode.util.Image_Generate_Util.Base_CompyUI_Generate_Util import Base_Compy_UI_Util
from enum import Enum
import MyCode.util.Video_Edit_Util.VideoComposer as VideoComposer
import MyCode.util.Image_Generate_Util.GetPathFromPrompt_ID as GetPathFromPrompt_ID
from MyCode.util.Music_Chioce_Util.Music_Util import Music_Util
import time
import datetime
from MyCode.util.self_requestUtil.RequestForArticle import RequestForArticle
import pymysql

# ==== 数据库连接配置 ====
HOST = "localhost"
PORT = 3306
USER = "algernon"
PASSWORD = "123"
DB = "testdb"

class StylizedModel(Enum):
    # 枚举成员：格式 成员名 = 值，值可以是 数字/字符串/对象 等任意类型
    GuFeng =  Local_Image_WorkFlow("")

# class SumService(BaseService):
#     def __init__(self,requestUtil:Base_Request,TTSUtil:Base_Audio_Util,SubtitleUtil:Base_Subtitle_Util,music_util:Music_Util):
#         self.RU=requestUtil
#         self.TTS=TTSUtil
#         self.SU=SubtitleUtil
#         self.MU=music_util
#         self.UID2Video_Id: dict[int, list[str]] = {}

#     def run(self,content):
#         db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")
#         video_id=int(time.time())
#         response= self.RU.request(content)
#         json_list = self_parse(response,video_id,0)
#         uid=0
#         self.UID2Video_Id[video_id]=[]
#         os.makedirs(f"/article/video/temp/",exist_ok=True)
#         for item in json_list:
#             #背景音乐
#             mood:str=item["mood"]
#             videoName=f"{video_id}_{uid}"
#             self.UID2Video_Id[video_id].append(str(videoName))
#             #生成配音
#             audio_path= self.TTS.audio_request(videoName,item["scene"])
            
#             srt_path= self.SU.generate_src(videoName,item["scene"])
#             theme = str(item['theme_id'])
#             # 插入数据库，并把 step 设置为 1
#             db.insert_video({
#                 "video_id": video_id,
#                 "uid": uid,
#                 "theme": theme,
#                 "scene": item["scene"],
#                 "src_path": srt_path,
#                 "audio_path": audio_path,
#                 "mood": mood,
#                 "step": 1
#             })
#             uid+=1
def run_sum_service(content, requestUtil, TTSUtil, SubtitleUtil):
    db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")

    video_id = int(time.time())
    response = requestUtil.request(content)
    json_list = self_parse(response, video_id, 0)

    UID2Video_Id: dict[int, list[str]] = {}
    UID2Video_Id[video_id] = []

    os.makedirs("/article/video/temp/", exist_ok=True)

    uid = 0
    for item in json_list:
        mood: str = item["mood"]
        videoName = f"{video_id}_{uid}"
        UID2Video_Id[video_id].append(videoName)
        audio_path = TTSUtil.audio_request(videoName, item["scene"])
        srt_path = SubtitleUtil.generate_src(videoName, item["scene"])
        theme = str(item["theme_id"])
        db.insert_video({
            "video_id": video_id,
            "uid": uid,
            "theme": theme,
            "scene": item["scene"],
            "src_path": srt_path,
            "audio_path": audio_path,
            "mood": mood,
            "step": 1
        })
        uid += 1

    return UID2Video_Id

def getImage():
    db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")

    # 1️⃣ 查询所有 step=1 的记录
    step1_videos = db.get_pending_videos(step=1)

    for video in step1_videos:
        id=video['id']
        video_id = video["video_id"]
        uid = video["uid"]
        scene = video["scene"]
        theme=video["theme"]
        videoName = f"{video_id}_{uid}"
        base: Base_Image_Generate_Util = StylizedModel[str(theme)].value
        video_generate:Base_Video_Util=  Base_Direct_Generate_Util(base,RU=RequestAI())
        paths: list[str] = video_generate.generateFrame(scene)

        # 4️⃣ 将帧路径或主要信息写回数据库
        # 假设我们存 video_path 作为生成帧的临时路径
        # 或者你可以单独存 paths 的 JSON
        video_path = ",".join(paths)  # 简单存储为逗号分隔路径
        db.update_field(id=id,field="video_path" ,value=video_path)
        # 5️⃣ 更新 step=2
        db.update_step(id, 2)
        print(f"Video {video_id} uid={uid}: {len(paths)} frames generated, step updated to 2")

import os
from collections import defaultdict
import time

def getVideo():
    db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")

    # 1️⃣ 查询所有 step=2 的记录
    step2_videos = db.get_pending_videos(step=2)
    
    # 2️⃣ 按 video_id 分组，并按 uid 排序
    video_dict = defaultdict(list)
    for video in step2_videos:
        video_dict[video["video_id"]].append(video)

    for video_id in sorted(video_dict.keys()):
        video_dict[video_id].sort(key=lambda x: x["uid"])

    # 3️⃣ 遍历每个视频的片段
    for video_id, videos in video_dict.items():
        for video in videos:
            uid = video["uid"]
            # 从数据库获取必要路径
            paths:list[str] = video["video_path"].split(",")      # 帧列表
            audio_path = video["audio_path"]           # 配音路径
            srt_path = video["src_path"]               # 字幕路径
            music_path = video.get("music_path", None) # 背景音乐，可选

            # 临时和最终视频路径
            temp_video_path = f"/article/video/temp/{video_id}_{uid}.mp4"
            final_output_path = f"/article/video/{video_id}_{uid}.mp4"
            os.makedirs("/article/video/temp", exist_ok=True)
            os.makedirs("/article/video", exist_ok=True)
            # 实际生成逻辑可替换为：
            VideoComposer.images_to_video(paths, audio_path, temp_video_path)
            VideoComposer.add_subtitles(temp_video_path, srt_path, temp_video_path)
            if music_path:
                VideoComposer.add_audio_to_video(temp_video_path, music_path, final_output_path, 0.5)

            # 5️⃣ 更新数据库 step=3，并写入 output_path
            db.upsert_video_field(video_id=video_id, uid=uid, field="step", value=3)
            db.upsert_video_field(video_id=video_id, uid=uid, field="output_path", value=final_output_path)

            print(f"Video {video_id} uid={uid} processed, step updated to 3, output_path set.")
    
    db.close()


if __name__ == '__main__':

        SubtitleUtil=Whisper_Sybtitle_Util(),
        TTSUtil=Edge_TTS_Util(),
        requestUtil=RequestForArticle(),
        music_util=Music_Util()
    