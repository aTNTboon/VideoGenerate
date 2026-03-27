import os
import random

from MyCode.config.music_catalog import MUSIC_BY_MOOD


def generate_music(mood: int) -> str | None:
    path = MUSIC_BY_MOOD.get(mood)
    if not path:
        return None

    files: list[str] = os.listdir(path)
    if not files:
        return None

    chosen_file = random.choice(files)
    return os.path.join(path, chosen_file)
