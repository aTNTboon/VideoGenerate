from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.Image_Generate_Util.Base_Video_Util import Base_Video_Util
from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.Image_Generate_Util.dircect_generate import generate_images_from_diffusers
class Base_Direct_Generate_Util(Base_Video_Util):
    def __init__(self,Base_Image_Generate_Util:Base_Image_Generate_Util,RU:Base_Request):
        self.BIGU=Base_Image_Generate_Util
        self.RU=RU
        pass
    
    def generateFrame(self,content)->list[str]:
        text=""
        with open("/article/MyCode/prompt/picture_generate.txt","r") as f:
            text=f.read()
        text+=content
        response= self.RU.request(text)
        posivite_promp= ""
        try:
            start=0
            end:int=response.find("|")
            promps:list[str]=[]
            while end!=-1:
                posivite_promp= response[start:end]
                response=response[end:]
                start=0
                promps.append(posivite_promp)
            paths:list[str] = generate_images_from_diffusers(prompts=promps)
            return paths
        except Exception as e:
            raise Exception("产图问题")






    