
from MyCode.Setting import Setting

class Base_Image_Generate_Util:
    def __init__(self,path):
        if path==None|path=="":
            self.path=path
        else:
            self.path=Setting.WorkFlows[0]
        pass

    def getImage(self) -> str:
        raise NotImplementedError
    