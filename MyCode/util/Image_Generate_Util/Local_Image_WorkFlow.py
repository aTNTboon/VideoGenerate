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
        print("self.path",self.path)

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
        return prompt_id


