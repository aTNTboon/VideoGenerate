
import uuid
import re
import Setting

from BaseService import  BaseService

class SecenePaser(BaseService):
    def __init__(self,uid):
        self.uid=uid
        self.theme=-1
        self.parse()

    def parse(self):
        text = ""
        with open(f"./story/{self.uid}.txt", "r", encoding="utf-8") as f:
           text = f.read()

        text = text.strip()
        m = re.search(r"<theme>(\d+)</theme>", text)

        theme_id=self.theme
        if(theme_id<0): 
            if m:
                theme_id = int(m.group(1))
        m=re.search(r'<story>(.*)</story>', text,re.DOTALL)
        if not m:
            raise Exception("no story")
        scenes_txt=m.group(1)
        if not scenes_txt:
            raise Exception('no scene')
        scenes = re.findall(r'<scene\s+mood="(\d+)">(.*?)</scene>', scenes_txt, re.DOTALL)
        json_list = []
        for mood, scene_text in scenes:
            json_list.append({
                "uid": uid,
                "theme_id": theme_id,
                "mood": int(mood),
                "scene": scene_text.strip()  # 去掉首尾空格
            })
        self.json=json_list
    def run(self):
        return self.json

if __name__ == '__main__':
    uid=1
    json={}
    try:
        parser = SecenePaser(uid)
        json=parser.run()

    except Exception as e:
        print(e)