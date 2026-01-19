
from MyCode.Setting import Setting
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.self_requestUtil.Base_Request import Base_Request

class Base_Video_Generate_Util:
    def __init__(self,Base_Image_Generate_Util:Base_Image_Generate_Util,RU:Base_Request):
        self.BIGU=Base_Image_Generate_Util
        self.RU=RU
        pass
    def generateFrame(self,videoName,content)->list[str]:
        text=""
        with open("/article/MyCode/prompt/picture_generate.txt","r") as f:
            text=f.read()
        text+=content
        response= self.RU.request(text)
        posivite_promp= ""
        try:
            posivite_promp= response[0:response.find("|")]
        except Exception as e:
            posivite_promp= ""
            print(e)
        try:
            nagitive_prompt=response[response.find("|")+1:]
        except Exception as e:
            nagitive_prompt= ""
            print(e)
        
        return self.BIGU.getImage(videoName,posivite_promp,nagitive_prompt)




    