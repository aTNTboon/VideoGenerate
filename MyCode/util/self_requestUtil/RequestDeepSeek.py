from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.self_requestUtil.deepseek.deepseek import call_chat_api


class RequestDeepSeek(Base_Request):
    def __init__(self):
        pass

    def request(self, message) -> str:
        return call_chat_api(message)
