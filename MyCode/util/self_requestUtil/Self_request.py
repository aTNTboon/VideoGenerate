import json
import requests
from  MyCode.Setting import Setting
from Base_Request import Base_Request

class RequestAI(Base_Request):
    def __init__(self) -> None:
        pass
    
    def getResonce(self,message)->str:

        headers = {
        "Authorization": f"{Setting.ApiKey}:{Setting.ApiSecret}",
        "content-type": "application/json"
    }
        payload = {
        "model": "x1",
        "user": "user_id",
        "messages": [
            {
                "role": "user",
                "content": f"{message}"
            }
        ],
        "stream": True,
        "tools": [
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode": "deep"
                }
            }
        ]
    }
        response = requests.post(
            url=Setting.ApiUrl,
            headers=headers,
            data=json.dumps(payload),
            stream=False
        )
        for chunks in response.iter_lines():
            # 打印返回的每帧内容
            # print(chunks)
            if (chunks and '[DONE]' not in str(chunks)):
                data_org = chunks[6:]

                chunk = json.loads(data_org)
                text = chunk['choices'][0]['delta']
                # 判断最终结果状态并输出
                if ('content' in text and '' != text['content']):
                    content = text["content"]
                    if (True == isFirstContent):
                        isFirstContent = False
                    full_response += content
                    print(full_response)
        return full_response