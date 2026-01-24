import ast
from MyCode.Setting import Setting
from MyCode.util.Image_Generate_Util import GetPathFromPrompt_ID
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
import os
import requests
import json

import random

class Local_Image_WorkFlow(Base_Image_Generate_Util):
    def getImage(self,posivite_promp,nagitive_prompt)->list[str]:


        workflow_file = self.path
        http_url = f"{Setting.CompyPromptUrl}/prompt"
        print("self.path",self.path)

        # --- 生成 client_id ---
        # --- 读取 workflow ---
        with open(workflow_file, "r", encoding="utf-8") as f:
            workflow = f.read()
# 替换宽高、正向/反向提示词
        workflow= str(workflow).replace("</height>",str(Setting.height))
        workflow= workflow.replace("</width>",str(Setting.width))
        
        workflow= workflow.replace("</posivite>",posivite_promp) # 修正拼写
        workflow= workflow.replace("</nagitive>",nagitive_prompt)
        seed= random.randint(0, 2**48 - 1)
        workflow = workflow.replace("</seed>",str(seed))
        # ✅ 终极修复：将Python字典字符串转回字典
        workflow_json = json.loads(workflow)
        payload = {
            "prompt": workflow_json,
            "client_id": client_id
        }
        print(workflow)
        resp = requests.post(http_url, json=payload)
        prompt_id = resp.json()["prompt_id"]
        print("Prompt ID:", prompt_id)
        ids:list[str]=[]
        ids.append(prompt_id)
        paths:list[str]=[]
        for prompt_id in ids:
            path = GetPathFromPrompt_ID.get_path_from_Prompt_id(prompt_id)
            paths.append(path)
        return paths


if __name__ == '__main__':


    local_image_workflow = Local_Image_WorkFlow("")
    local_image_workflow.getImage("test",
    "pussy,dick,sex,realistic style，4-panel comic layout, quad split screen,clear facial features,eye contact with viewer,uniform white stockings,sweet lolita white hosiery,white stokings,masterpiece, best quality, absurdres, highres,beautiful, very awa,nsfw,green and white hair","")
    