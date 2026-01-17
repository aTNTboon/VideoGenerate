import edge_tts


class Base_Audio_Util:
    def __init__(self):
        pass

    def audio_request(self, story) -> str:
        raise NotImplementedError