
from MyCode.Setting import Setting

class Base_Image_Generate_Util:
    def __init__(self,path):
        if not path or path=="":
            self.path=Setting.WorkFlows[0]
            
        else:
            self.path=path
        pass

    def getImage(self,uid,posivite_promp,nagitive_prompt):
        raise NotImplementedError
    