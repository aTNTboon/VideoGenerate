from MyCode.util.Image_Generate_Util.Base_Video_Util import Base_Video_Util
from MyCode.util.self_requestUtil.Base_Request import Base_Request


class Base_Direct_Generate_Util(Base_Video_Util):
    def __init__(self, RU: Base_Request):
        self.RU = RU
        pass

    def generateFrame(self, content):
        text = ""
        with open("/article/MyCode/prompt/picture_generate.txt", "r") as f:
            text = f.read()
        text += content
        response = self.RU.request(text)
        posivite_promp = ""
        try:
            start = 0
            end: int = response.find("|")
            promps: list[str] = []
            while end != -1:
                if end >= len(response):
                    break
                posivite_promp = response[start:end]
                response = response[end + 1 :]
                start = 0
                end = int(response.find("|"))
                promps.append(posivite_promp)
            return promps
        except Exception as e:
            raise Exception("产图问题", e)
