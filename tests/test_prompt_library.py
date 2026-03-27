from MyCode.config.music_catalog import MUSIC_BY_MOOD
from MyCode.config.style_catalog import STYLE_NAME_BY_THEME
from MyCode.core.library.prompt_library import PromptLibrary


def test_prompt_library_contains_expected_style_keywords():
    assert "futuristic" in PromptLibrary.get_style_keywords("科技")
    assert "hand-drawn" in PromptLibrary.get_style_keywords("手绘")
    assert "warm tone" in PromptLibrary.get_style_keywords("温暖")


def test_prompt_library_formats_scene_with_text_field():
    result = PromptLibrary.format_scene_context(
        text="数据库文本", scene="主角走入城市", style_name="科技"
    )
    assert "数据库文本" in result
    assert "主角走入城市" in result
    assert "futuristic" in result


def test_style_and_music_catalogs_extracted_from_setting():
    assert STYLE_NAME_BY_THEME[1] == "科技"
    assert MUSIC_BY_MOOD[1] is not None
