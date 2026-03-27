import gc
import os
from MyCode.Setting import Setting
from MyCode.sqlManager import VideoDBManager
from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util
from MyCode.util.Image_Generate_Util import generate_Image
from MyCode.util.Image_Generate_Util.Base_Direct_Generate_Util import (
    Base_Direct_Generate_Util,
)
from collections import defaultdict
from MyCode.util.Image_Generate_Util.Base_Video_Util import Base_Video_Util
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.util.Subtitle_Util.Get_Subtitle import Get_SubTitle_Util
from MyCode.util.SceneParser import self_parse
import MyCode.util.Video_Edit_Util.VideoComposer as VideoComposer
import time
from typing import Type
from typing import Dict
from MyCode.util.Music_Chioce_Util.Music_Util import generate_music
from MyCode.util.self_requestUtil.RequestDeepSeek import RequestDeepSeek
from MyCode.util.self_requestUtil.RequestForArticle import RequestForArticle
from MyCode.config.style_catalog import STYLE_NAME_BY_THEME
from MyCode.core.library.prompt_library import PromptLibrary

# ==== 数据库连接配置 ====
HOST = "localhost"
PORT = 3306
USER = "algernon"
PASSWORD = "123"
DB = "testdb"

# 枚举成员：格式 成员名 = 值，值可以是 数字/字符串/对象 等任意类型

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
def run_sum_service(
    db: VideoDBManager, content, requestUtil, audio_service, SubtitleUtil, name: str
):
    video_id = int(time.time())
    response = requestUtil.request(content)
    json_list = self_parse(response, 0)

    os.makedirs("/article/video/temp/", exist_ok=True)
    for item in json_list:
        mood: str = item["mood"]
        uid = item["uid"]
        videoName = f"{video_id}_{uid}"
        if item["scene"] == "":
            continue
        if hasattr(audio_service, "create_voice"):
            audio_path = audio_service.create_voice(videoName, item["scene"])
        else:
            audio_path = audio_service.audio_request(videoName, item["scene"])
        srt_path = SubtitleUtil.generate_src(videoName, item["scene"])

        theme = int(item["theme_id"])
        db.insert_video(
            {
                "video_id": video_id,
                "uid": uid,
                "theme": theme,
                "scene": item["scene"],
                "src_path": srt_path,
                "audio_path": audio_path,
                "mood": mood,
                "step": 1,
                "text": name,
            }
        )


def getprompt(db: VideoDBManager, ba: Type[Base_Video_Util]):
    step1_videos = db.get_pending_videos(step=1)
    temp_scenes: str = ""
    ids: list[int] = []
    amount: int = 0
    video_generate: Base_Video_Util = ba(RU=RequestDeepSeek())
    for video in step1_videos:
        id: int = int(video["id"])
        if temp_scenes != "":
            temp_scenes += "|"

        scene = str(video.get("scene", ""))
        text = str(video.get("text", ""))
        theme = int(video.get("theme", 0) or 0)
        style_name = STYLE_NAME_BY_THEME.get(theme, "温暖")

        if scene == "":
            continue
        merged_scene = PromptLibrary.format_scene_context(text=text, scene=scene, style_name=style_name)
        temp_scenes = temp_scenes + merged_scene
        amount += 1
        ids.append(id)
        if amount >= 8:
            temp_scenes = temp_scenes + "|"
            amount = 0
            getBatchpro(ids, video_generate, temp_scenes, db)
            temp_scenes = ""
    if temp_scenes != "":
        temp_scenes = temp_scenes + "|"
        getBatchpro(ids, video_generate, temp_scenes, db)


def getBatchpro(
    ids: list[int],
    video_generate: Base_Video_Util,
    temp_scenes: str,
    db: VideoDBManager,
):
    prmts: list[str] = video_generate.generateFrame(temp_scenes)
    idx = 0
    prop = ""
    for id in ids:
        if idx < len(prmts):
            prop = prmts[idx]
        db.update_field(id=id, field="prompts", value=prop)
        db.update_step(id, 2)
        idx += 1

    ids.clear()


def getImage(db: VideoDBManager):

    # 1️⃣ 查询所有 step=1 的记录
    step1_videos = db.get_pending_videos(step=2)
    video_map: Dict[int, str] = {}
    for video in step1_videos:
        video_id = video["id"]
        promt = video["prompts"]
        video_map[video_id] = promt
    paths: Dict[int, str] = generate_Image.remote_generate_anime_images(
        prompts=video_map
    )
    for id in paths.keys():
        video_path = paths[id]  # 简单存储为逗号分隔路径
        if video_path and video_path != "":
            db.update_field(id=id, field="video_path", value=video_path)
            # 5️⃣ 更新 step=2
            db.update_step(id, 3)
        print(f"Video {id} frames generated, step updated to ")





def getVideo(db: VideoDBManager, video_editor=VideoComposer):

    # 1️⃣ 查询所有 step=2 的记录
    step2_videos = db.get_pending_videos(step=3)

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
            id = video["id"]

            # 从数据库获取必要路径
            paths: list[str] = video["video_path"].split(",")  # 帧列表
            audio_path = video["audio_path"]  # 配音路径
            srt_path = video["src_path"]  # 字幕路径

            # 临时和最终视频路径
            temp_video_path = f"/article/video/temp/{video_id}_{uid}.mp4"
            temp_sub_video_path = f"/article/video/sub/{video_id}_{uid}.mp4"
            os.makedirs("/article/video/temp", exist_ok=True)
            os.makedirs("/article/video", exist_ok=True)
            os.makedirs("/article/video/sub", exist_ok=True)
            # 实际生成逻辑可替换为：
            video_editor.images_to_video(paths, audio_path, temp_video_path)
            video_editor.add_subtitles(temp_video_path, srt_path, temp_sub_video_path)
            os.remove(temp_video_path)

            db.update_field(id, "output_path", temp_sub_video_path)
            db.update_step(id, 4)


def concat(db: VideoDBManager):
    """Step‑1: take all rows at step=4, merge per video_id, insert into finishedVideo and update step."""
    results = db.get_pending_videos(step=4)
    if not results:
        return

    grouped_paths = defaultdict(list)
    grouped_meta = {}
    ids: list[int] = []

    for row in results:
        vid = row["video_id"]
        grouped_paths[vid].append(row["output_path"])
        ids.append(row["id"])
        if vid not in grouped_meta:
            grouped_meta[vid] = {
                "text": row.get("text", ""),
                "mood": row.get("mood", ""),
            }

    # merge each chunk, write to finishedVideo
    for vid, paths in grouped_paths.items():
        meta = grouped_meta.get(vid, {})
        text = meta.get("text", "")
        mood = meta.get("mood", "")
        final_path = VideoComposer.concatVideos(paths, vid, None)
        try:
            db.insert_finished_video(vid, text, mood, final_path)
        except Exception as e:
            print(f"insert_finished_video failed for video {vid}: {e}")

    # mark original rows as completed (step=5)
    for _id in ids:
        try:
            db.update_step(_id, 5)
        except Exception as e:
            print(f"update_step failed for id {_id}: {e}")


def concatVideos(db: VideoDBManager):
    """Step‑2: load finishedVideo entries, group by text and merge into final clips.

    When merging per-text groups we select the mood of the first record in the
    group and use it to generate a background music track for the final merge.
    """
    rows = db.query_finished_videos()
    if not rows:
        return

    # build groups and remember first mood for each text key
    grouped = defaultdict(list)
    first_mood: Dict[str, str] = {}
    for r in rows:
        txt = r.get("text", "")
        path = r.get("videoPath")
        if not path:
            continue

        grouped[txt].append(path)
        if txt not in first_mood:
            first_mood[txt] = r.get("mood", "")

    for txt, paths in grouped.items():
        mood = first_mood.get(txt, "-1")
        m = int(mood)
        music_path = generate_music(m) if m >= 0 else None
        # use text as identifier for the merged output
        result_path = VideoComposer.concatVideos(paths, txt, music_path)
        print(f'merged text="{txt}" into {result_path} (mood={mood})')


def Get_Video_With_AI_Image(name: str, txt: str):
    db = Setting.Ai_Video_DataBase
    SubtitleUtil: Base_Subtitle_Util = Get_SubTitle_Util()
    TTSUtil: Edge_TTS_Util = Edge_TTS_Util()
    requestUtil: RequestForArticle = RequestForArticle()
    run_sum_service(db, txt, requestUtil, TTSUtil, SubtitleUtil, name)
    if hasattr(SubtitleUtil, "close"):
        SubtitleUtil.close()
    if hasattr(TTSUtil, "close"):
        TTSUtil.close()
    if hasattr(requestUtil, "close"):
        requestUtil.close()
    del SubtitleUtil
    del TTSUtil
    del requestUtil
    gc.collect()
    getprompt(db, Base_Direct_Generate_Util)
    gc.collect()
    getImage(db)
    gc.collect()
    getVideo(db)
    concat(db)
    concatVideos(db)


def Get_Video_With_Video(name: str, txt: str):
    db = Setting.Direct_Video_DataBase
    SubtitleUtil: Base_Subtitle_Util = Get_SubTitle_Util()
    TTSUtil: Edge_TTS_Util = Edge_TTS_Util()
    requestUtil: RequestForArticle = RequestForArticle()
    run_sum_service(db, txt, requestUtil, TTSUtil, SubtitleUtil, name)
    if hasattr(SubtitleUtil, "close"):
        SubtitleUtil.close()
    if hasattr(TTSUtil, "close"):
        TTSUtil.close()
    if hasattr(requestUtil, "close"):
        requestUtil.close()
    del SubtitleUtil
    del TTSUtil
    del requestUtil
    gc.collect()
