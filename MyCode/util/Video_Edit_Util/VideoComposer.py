import os
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeAudioClip,
    TextClip,
    CompositeVideoClip
)
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout

from moviepy.audio.fx.volumex import volumex
import moviepy.video.tools.subtitles as mp_sub
from typing import List


    # ---------------- 功能 1 ----------------
def images_to_video(images: List[str], audio_path: str, output_path: str, image_volume: float = 1.0):
        """
        images: 图片路径列表
        audio_path: 背景音频路径
        image_volume: 音频音量倍数
        """
        audio = AudioFileClip(audio_path).fx(volumex, image_volume)
        duration = audio.duration
        num_images = len(images)
        img_duration = duration / max(num_images, 1)

        clips = [ImageClip(img).set_duration(img_duration) for img in images]
        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio)
        video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
        for clip in clips:
            clip.close()

    # ---------------- 功能 2 ----------------
def add_audio_to_video(video_path: str, new_audio_path: str, output_path: str, new_audio_volume: float = 1.0):
        """
        video_path: 原视频路径
        new_audio_path: 新音频路径
        new_audio_volume: 新音频音量倍数
        """
        video = VideoFileClip(video_path)
        duration = video.duration
        new_audio:AudioFileClip = AudioFileClip(new_audio_path).fx(volumex, new_audio_volume)
        new_audio.subclip(0, duration)
        new_audio = new_audio.fx(audio_fadein, 2.0)
        new_audio = new_audio.fx(audio_fadeout, 2.0)
        if video.audio:
            mixed_audio = CompositeAudioClip([video.audio, new_audio])
        else:
            mixed_audio = new_audio

        video = video.set_audio(mixed_audio)
        video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)

    # ---------------- 功能 3 ----------------
def add_subtitles( video_path: str, srt_path: str, output_path: str):
        """
        video_path: 视频路径
        srt_path: 字幕文件路径
        """
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        video = VideoFileClip(video_path)
        generator = lambda txt: TextClip(
            txt,
            font=font_path,
            fontsize=36,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(1280, 100),  # 宽度优先，高度自动换行
            align='center'      # 水平对齐
            )

        subs:mp_sub.SubtitlesClip = mp_sub.SubtitlesClip(srt_path, generator)

        subs = subs.set_position(("center", "bottom"))
        final = CompositeVideoClip([video, subs])
        if video.audio:
            final = final.set_audio(video.audio)

        final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)
        


if __name__ == '__main__':
    try:
        path=os.path.join("/article/MyCode/movie", "output.mp4")
        # images_to_video(["/article/MyCode/image/ComfyUI_00002_.png", "/article/MyCode/image/ComfyUI_00265_.png"], "/article/audio/test.wav", path,1.0)
        # add_audio_to_video(path,"/article/music/test.mp3", path,0.2)
        add_subtitles(path,"/article/subtitle/test.srt",     os.path.join("/article/MyCode/movie", "output11.mp4"))
    except Exception as e:
        print(e)