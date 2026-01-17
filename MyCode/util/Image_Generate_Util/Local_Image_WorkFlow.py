from MyCode.Setting import Setting
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
import os
import requests
import json
import uuid
import time
import websocket


class Local_Image_WorkFlow(Base_Image_Generate_Util):
    def getImage(self,uid,prompt:list[str]):
        client_id = uid
        workflow_file = self.path
        ws_url_template =f"{Setting.CompyPath}?clientId={client_id}"
        http_url = f"{Setting.CompyPromptUrl}/prompt"

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
        history = requests.get(f"{Setting.CompyPromptUrl}history/{prompt_id}").json()
        # --- 获取图片文件名示例 ---
        history=history[prompt_id]
        image_path=Setting.ImagePath+str(uid)
        os.makedirs(image_path, exist_ok=True)
        if history.get("outputs"):
            for node_id, output in history["outputs"].items():
                if "images" in output:
                    for img_info in output["images"]:
                        filename = img_info["filename"]
                        output =os.path.join(image_path,filename)
                        input= os.path.join("/comfyUIProject/ComfyUI/output/"+filename)
                        with open(input,"rb") as f:
                            fi=f.read()
                            with open(output,"wb")as w:
                                w.write(fi)
