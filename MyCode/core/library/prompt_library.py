from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    content: str


class PromptLibrary:
    """Central prompt templates + style keyword library."""

    _templates = {
        "article_generate": PromptTemplate(
            name="article_generate",
            content=(
                "请将以下文本拆分为分镜。返回格式必须包含<theme>与<story>，并且每行故事要包含情绪标签。\n"
            ),
        ),
        "picture_generate": PromptTemplate(
            name="picture_generate",
            content=(
                "你是影视分镜提示词生成器。请针对每个片段输出一条英文绘图提示词，片段之间使用|分隔。"
                "提示词必须包含主体、环境、镜头、光线、风格关键词。\n"
            ),
        ),
    }

    _style_keywords = {
        "古风": "ancient chinese style, elegant costume, ink atmosphere",
        "科技": "futuristic tech, neon light, cyber city",
        "手绘": "hand-drawn, sketch texture, watercolor stroke",
        "温暖": "warm tone, soft sunlight, cozy ambience",
    }

    @classmethod
    def get_template(cls, key: str) -> str:
        if key not in cls._templates:
            raise KeyError(f"未知提示词模板: {key}")
        return cls._templates[key].content

    @classmethod
    def get_style_keywords(cls, style_name: str) -> str:
        return cls._style_keywords.get(style_name, cls._style_keywords["温暖"])

    @classmethod
    def format_scene_context(cls, text: str, scene: str, style_name: str) -> str:
        style = cls.get_style_keywords(style_name)
        return f"文本:{text}; 场景:{scene}; 风格:{style}"
