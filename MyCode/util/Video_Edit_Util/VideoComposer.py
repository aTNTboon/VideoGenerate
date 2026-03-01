import math
import os

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    CompositeAudioClip,
    TextClip,
    CompositeVideoClip,
    concatenate_audioclips,
)
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout

from moviepy.audio.fx.volumex import volumex
import moviepy.video.tools.subtitles as mp_sub
from typing import List
from moviepy.video.fx import resize as vfx_resize
import random
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from moviepy.audio.fx.volumex import volumex
from PIL import Image


def images_to_video(images: list[str], audio_path, output_path, image_volume=1.0):
    audio = AudioFileClip(audio_path).fx(volumex, image_volume)
    duration = audio.duration
    num_images = len(images)
    img_duration = duration / max(num_images, 1)

    first_img = Image.open(images[0])
    video_size = first_img.size
    first_img.close()

    W, H = video_size
    move_pixels = int(W * 0.05)  # 平移幅度（5%宽度）
    zoom_factor = 1.10  # 放大 10% 防止黑边
    clips = []
    if hasattr(Image, "Resampling"):
        Image.ANTIALIAS = Image.Resampling.LANCZOS  # type: ignore

    # 对于每张图片，添加平滑过渡，随机微量平移和缩放
    for i, img in enumerate(images):
        # horizontal or vertical shift
        horiz = random.choice([-1, 0, 1])
        vert = random.choice([-1, 0, 1])
        start_x = horiz * move_pixels
        start_y = vert * move_pixels
        end_x = -start_x
        end_y = -start_y

        # random slight zoom factor between 1.0 and 1.05 (可小于1为缩小)
        local_zoom = zoom_factor * random.uniform(0.98, 1.05)

        # 平滑过渡：插值函数同时处理 x 和 y
        def make_pos(t, sx=start_x, sy=start_y, ex=end_x, ey=end_y):
            progress = 0.5 - 0.5 * math.cos(math.pi * (t / img_duration))
            x = sx + (ex - sx) * progress
            y = sy + (ey - sy) * progress
            return ("center", x, y)

        # 创建视频剪辑并添加效果
        clip = (
            ImageClip(img)
            .fx(vfx_resize.resize, local_zoom)  # 微量缩放
            .set_start(i * img_duration)
            .set_duration(img_duration)
            .set_position(make_pos)
        )

        clips.append(clip)

    video = CompositeVideoClip(clips, size=video_size).subclip()
    video = video.set_audio(audio)
    # trim 0.15 seconds from start and end to avoid trailing silence/blank
    if video.duration and video.duration > 0.3:
        video = video.subclip(0.15, video.duration - 0.15)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    for clip in clips:
        clip.close()
    audio.close()
    video.close()
    for image in images:
        os.remove(image)

    os.remove(audio_path)

    # ---------------- 功能 2 ----------------


def add_audio_to_video(
    video_path: str,
    new_audio_path: str,
    output_path: str,
    new_audio_volume: float = 0.2,
):

    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(new_audio_path).fx(volumex, new_audio_volume)

    if video.audio is None:
        # 没有原音频，直接加
        video = video.set_audio(new_audio)
        video.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=video.fps
        )
        return

    # 混音时长 = 新音频长度 或 视频长度 中较小者
    mix_duration = min(video.duration, new_audio.duration)

    # ===== 第一段：混音 =====
    base_part = video.audio.subclip(0, mix_duration)
    new_part = new_audio.subclip(0, mix_duration)

    new_part = new_part.fx(audio_fadein, 2.0)
    new_part = new_part.fx(audio_fadeout, 2.0)

    mixed_part = CompositeAudioClip([base_part, new_part])

    # ===== 第二段：原音频剩余部分 =====
    # if video.duration > mix_duration:
    #     remain_part = video.audio.subclip(mix_duration, video.duration)

    #     # 把第二段接在后面
    #     final_audio = concatenate_audioclips([mixed_part, remain_part])
    # else:
    #     final_audio = mixed_part

    # final_audio = final_audio.set_duration(video.duration)

    video = video.set_audio(mixed_part)

    video.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=video.fps
    )

    # ---------------- 功能 3 ----------------


def add_subtitles(video_path: str, srt_path: str, output_path: str):
    """
    video_path: 视频路径
    srt_path: 字幕文件路径
    """
    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    video = VideoFileClip(video_path)
    generator = lambda txt: TextClip(
        txt,
        font=font_path,
        fontsize=20,
        color="white",
        method="caption",
        size=(600, 300),  # 宽度优先，高度自动换行
        align="center",  # 水平对齐
    )
    with open(srt_path, "r", encoding="utf-8") as f:
        txt = f.read().strip()
        print(txt)

    # 检查 SRT 是否至少有两条字幕
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    # 如果小于 4 行（序号 + 时间码 + 文本 + 空行），直接用 TextClip 替代 SubtitlesClip
    if len(lines) < 4:
        subs = (
            generator(txt)
            .set_duration(video.duration)
            .set_position(("center", "bottom"))
        )
    else:
        subs: mp_sub.SubtitlesClip = mp_sub.SubtitlesClip(srt_path, generator)
        subs = subs.set_position(("center", "bottom"))

    final = CompositeVideoClip([video, subs])
    if video.audio:
        final = final.set_audio(video.audio)

    final.write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=video.fps
    )
    os.remove(srt_path)


def concatVideos(video_file: list[str], video_name: str, music_path: str | None):
    from moviepy.editor import VideoFileClip, concatenate_videoclips

    # 视频文件列表

    # 1. 读取所有视频
    clips = [VideoFileClip(f) for f in video_file]

    # 2. 拼接
    final_clip = concatenate_videoclips(
        clips, method="compose"
    )  # method="compose" 保证不同分辨率可以拼接
    # trim 0.15s from start and end
    if final_clip.duration and final_clip.duration > 0.3:
        final_clip = final_clip.subclip(0.15, final_clip.duration - 0.15)

    os.makedirs("/article/result", exist_ok=True)
    os.makedirs("/article/result/temp", exist_ok=True)
    temp_output = f"/article/result/temp/{video_name}.mp4"
    output = f"/article/result/{video_name}.mp4"
    # 3. 输出
    final_clip.write_videofile(temp_output, codec="libx264", audio_codec="aac", fps=24)
    for clip in clips:
        clip.close()
    for f in video_file:
        os.remove(f)
    if music_path != None and music_path != "":
        add_audio_to_video(temp_output, music_path, output, 0.5)
        os.remove(temp_output)
        return output
    return temp_output


if __name__ == "__main__":
    # try:
    #     path=os.path.join("/article/MyCode/movie", "output.mp4")
    #     # images_to_video(["/article/MyCode/image/ComfyUI_00002_.png", "/article/MyCode/image/ComfyUI_00265_.png"], "/article/audio/test.wav", path,1.0)
    #     # add_audio_to_video(path,"/article/music/test.mp3", path,0.2)
    #     add_subtitles(path,"/article/subtitle/test.srt", os.path.join("/article/MyCode/movie", "output11.mp4"))
    # except Exception as e:
    #     print(e)
    temp_output = "/article/result/1769656541.mp4"
    music_path = "/article/bgm/sad/兰琦&贺雨桐-认真的老去.mp3"
    output = "/article/result/test.mp4"
    add_audio_to_video(temp_output, music_path, output, 0.3)
