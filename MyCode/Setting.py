class Setting:
    ApiKey = "Bearer ZXSdpSgEJXFhygMYiiaA"
    ApiSecret = "jDalRRbmMsQBXJeiCUAa"
    ApiUrl = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    Model= "x1"
    VOICE= "zh-CN-XiaoxiaoNeural"
    SUBTITLE_MODEL="medium"
    WorkFlows=["/article/MyCode/workflows/ImageFlow/GuFeng.json"]
    CompyPath="ws://127.0.0.1:8188/ws"
    CompyPromptUrl='http://127.0.0.1:8188/'
    ImagePath="/article/image/"
    height=720
    width=1080
    style:dict[str,str]={
        "1":"GuFeng",
    }
    src_language="Chinese"
    role_name:str=""
    word_timestamps=False
    fp16=False