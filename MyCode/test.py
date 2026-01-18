# from MyCode.util.Audio_requestUtil.TTS_Util import Edge_TTS_Util

# Edge_TTS_Util().audio_request("test", "测试")


from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow


if __name__== '__main__':
    path=None
    l=Local_Image_WorkFlow(path=path)
    l.getImage(1,["a","b"])
