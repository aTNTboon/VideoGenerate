import os
import requests


import json
import websocket
from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow

def wait_queue_empty() -> bool:
    ws = websocket.WebSocket()
    ws.connect("ws://127.0.0.1:8188/ws")
    ws.settimeout(1)

    while True:
        try:
            raw = ws.recv()
        except websocket.WebSocketTimeoutException:
            continue  # ← 关键：超时就继续等

        if isinstance(raw, bytes):
            continue

        msg = json.loads(raw)
        if msg.get("type") == "status":
            if msg["data"]["status"]["exec_info"]["queue_remaining"] == 0:
                return True

def get_path_from_Prompt_id(prompt_id:str):

    history = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}").json()
    # --- 获取图片文件名示例 ---
    p:str=""
    history=history[prompt_id]
    if history.get("outputs"):
        for node_id, output in history["outputs"].items():
            if "images" in output:
                for img_info in output["images"]:
                    filename = img_info["filename"]
                    p= os.path.join("/comfyUIProject/ComfyUI/output/"+filename)
                    # with open(p,"rb") as f:
                    #     fi=f.read()
                    #     with open(filename,"wb")as w:
                    #         w.write(fi)
                    #         print('saved')
    return p


# if __name__ == '__main__':

    # for id in promptIds:
    # base:Local_Image_WorkFlow=Local_Image_WorkFlow("")
    # promptIds:list[str]= base.getImage("3456",
    #               "beautiful face,pussy,dick,sex,realistic style，4-panel comic layout, quad split screen,clear facial features,eye contact with viewer,uniform white stockings,sweet lolita white hosiery,white stokings,masterpiece, best quality, absurdres, highres,beautiful, very awa,nsfw,   green and white hair",
    #               "")
    # wait_queue_empty()
    #     temp_path=f"/article/image/test/{id}.png"
    #     path:str= get_path_from_Prompt_id(id)
    #     with open(temp_path,"wb") as t:
    #         with open(path,"rb") as f:
    #             t.write(f.read())
        