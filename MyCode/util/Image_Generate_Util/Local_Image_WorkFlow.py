import ast
from MyCode.Setting import Setting
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
import os
import requests
import json



class Local_Image_WorkFlow(Base_Image_Generate_Util):
    def getImage(self,uid:str,posivite_promp,nagitive_prompt):

        client_id = uid
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
        return prompt_id


if __name__ == '__main__':
    local_image_workflow = Local_Image_WorkFlow("")
    local_image_workflow.getImage("test","pussy,dick,sex,Woman on top,3p,Standing position,4-panel comic layout, quad split screen,clear facial features,eye contact with viewer,Profile full-body shot，uniform white stockings,  sweet lolita white hosiery,white stokings,masterpiece, best quality, absurdres, highres, very aesthetic, high quality, detailed, insanely detailed, beautiful, very awa, anime screencap,nsfw，Japanese anime fantasy illustration, pink-haired girl, wearing an ornate pink and white gradient kimono with golden embroidery and flowing ribbons, ethereal and alluring demeanor, soft dreamy color palette of pink, white, pale gold and lavender, set against a misty green mountain and cloud backgroung","")