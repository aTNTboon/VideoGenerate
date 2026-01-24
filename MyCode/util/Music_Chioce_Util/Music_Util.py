from MyCode.Setting import Setting
class Music_Util:
    def __init__(self):
        self.music_dict:dict[str,str]=Setting.music_dict

    def generate_music(self, text:str)->str:
        if  self.music_dict.get(text)!=None:
            return self.music_dict.get(text)
        else:
            return self.music_dict["1"]