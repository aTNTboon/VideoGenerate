import requests
import json
from MyCode.Setting import Setting


def call_chat_api(question: str) -> str:
    url = "https://dpapi.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Setting.apikey_deepseek}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-r1",
        "messages": [{"role": "user", "content": question}],
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.json()}")
    json_data = response.json()
    content = json_data["choices"][0]["message"]["content"]
    return content


# ------------------- 测试调用 -------------------
if __name__ == "__main__":
    # 提问内容：Windows录屏（Xbox Game Bar不可用）
    question = "Windows如何用自带工具录制桌面，Xbox Game Bar不能用的情况下"

    # 调用接口并打印结果
    answer = call_chat_api(question)
    print("=== 接口响应结果 ===")
    print(answer)
