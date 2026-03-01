from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VideoEntity:
    """
    videos数据表对应的实体类
    字段与数据表一一对应，默认值与insert_video方法保持一致
    """

    # 必选字段（无默认值，创建实例时必须传入）
    id: str = "0"
    video_id: str = "0"
    uid: str = "0"
    scene: str = ""
    src_path: str = ""
    audio_path: str = ""

    # 可选字段（带默认值，与原insert_video逻辑一致）
    theme: int = 0
    mood: int = 0
    music_path: str = ""
    video_path: str = ""
    output_path: str = ""
    step: int = 0
    prompts: str = ""
    text: str = "默认小说名"

    def to_dict(self) -> Dict[str, Any]:
        """
        将实体类对象转换为字典，方便直接传给insert_video方法
        :return: 字段名-值对应的字典
        """
        return {
            "video_id": self.video_id,
            "uid": self.uid,
            "theme": self.theme,
            "scene": self.scene,
            "src_path": self.src_path,
            "audio_path": self.audio_path,
            "mood": self.mood,
            "music_path": self.music_path,
            "video_path": self.video_path,
            "output_path": self.output_path,
            "step": self.step,
            "prompts": self.prompts,
            "text": self.text,
            "id": self.id,
        }
