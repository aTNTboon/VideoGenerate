
from MyCode.Setting import Setting
from MyCode.util.Image_Generate_Util import GetPathFromPrompt_ID
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.self_requestUtil.Base_Request import Base_Request

class Base_Video_Util:
    def __init__(self,Base_Image_Generate_Util:Base_Image_Generate_Util,RU:Base_Request):
        self.BIGU=Base_Image_Generate_Util
        self.RU=RU
        pass
    
    def generateFrame(self,videoName,content)->list[str]:
        raise Exception("unimplement")



    