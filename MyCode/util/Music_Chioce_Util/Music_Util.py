import os
import random
from MyCode.Setting import Setting

dict = Setting.music_dict


def generate_music(text: int) -> str | None:
    if dict.get(text) is not None:
        path = dict.get(text)
        files: list[str] = os.listdir(path)
        if path == None:
            return None
        # Ensure there are files in the directory
        if files:
            # Randomly choose one file from the list
            chosen_file = random.choice(files)
            return os.path.join(path, chosen_file)
        else:
            return None
    return None
