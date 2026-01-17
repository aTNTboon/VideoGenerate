import os
import requests
import json
import uuid
import time
import websocket
client_id = str(uuid.uuid4())
# --- 配置 ---
workflow_file = "./sese1 (Copy).json"
ws_url_template =f"ws://127.0.0.1:8188/ws?clientId={client_id}"
http_url = "http://127.0.0.1:8188/prompt"

# --- 生成 client_id ---


# --- 读取 workflow ---
with open(workflow_file, "r", encoding="utf-8") as f:
    workflow = json.load(f)

# --- 连接 WS ---
ws = websocket.WebSocket()
ws.connect(ws_url_template.format(client_id))
ws.settimeout(1)  # 防止死循环阻塞

# --- POST workflow ---
payload = {
    "prompt": workflow,
    "client_id": client_id
}
resp = requests.post(http_url, json=payload)
prompt_id = resp.json()["prompt_id"]
print("Prompt ID:", prompt_id)

# --- 等待完成 ---
finished = False
while not finished:
    try:
        msg = json.loads(ws.recv())
        if msg.get("type") == "executing":
            data = msg.get("data", {})
            # node==None 表示整个 workflow 执行完
            if data.get("node") is None and data.get("prompt_id") == prompt_id:
                finished = True
    except websocket.WebSocketTimeoutException:
        continue  # 超时就继续轮询

# --- 获取历史 / 输出信息 ---

finished = False
# --- 获取历史 / 输出信息 ---
history = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
# --- 获取图片文件名示例 ---
history=history[prompt_id]
if history.get("outputs"):
    for node_id, output in history["outputs"].items():
        if "images" in output:
            for img_info in output["images"]:
                filename = img_info["filename"]
                p= os.path.join("/comfyUIProject/ComfyUI/output/"+filename)
                with open(p,"rb") as f:
                    fi=f.read()
                    with open(filename,"wb")as w:
                        w.write(fi)
                        print('saved')