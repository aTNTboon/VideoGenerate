import os
import requests
import base64

# === 配置 API Key ===
API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not API_KEY:
    raise RuntimeError("请先设置环境变量 DASHSCOPE_API_KEY")

# === 接口地址: 中国北京地域 ===
URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# === 正向提示词 ===
prompt = """
一张风格清新精致的平面插画机器人，
白底，简洁线条，可爱表情，彩色矢量风格
"""

# === 请求体结构 ===
payload = {
    "model": "qwen-image-plus",   # 或 "qwen-image"
    "input": {
        "prompt": prompt,
        "negative_prompt": "低质量, 模糊, 失真",  # 不希望出现的内容
        "size": "1080*1920",       # 图像分辨率
        "prompt_extend": True,     # 启用自动润色优化提示词
        "watermark": False         # 是否加水印
    }
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# === 发起生成请求 ===
response = requests.post(URL, json=payload, headers=headers)
resp_json = response.json()

if response.status_code == 200:
    # 返回结果里可能是图片的 Base64
    img_b64 = resp_json.get("output", {}).get("results", [{}])[0].get("data")
    if img_b64:
        img_bytes = base64.b64decode(img_b64)
        with open("generated.png", "wb") as f:
            f.write(img_bytes)
        print("已保存生成图像: generated.png")
    else:
        print("未返回图片内容:", resp_json)
else:
    print("错误:", response.status_code, resp_json)
