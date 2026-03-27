import os

from MyCode.sqlManager import VideoDBManager


class Setting:
    ApiKey = "Bearer ZXSdpSgEJXFhygMYiiaA"
    ApiSecret = "jDalRRbmMsQBXJeiCUAa"
    ApiUrl = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    Model = "x1"
    image_api = "sk-ee359256b7da45d18462e9f854b756e0"
    VOICE = "zh-CN-YunxiNeural"
    PITCH = "+10Hz"
    RATE = "+12%"
    SUBTITLE_MODEL = "medium"
    WorkFlows = ["/article/MyCode/workflows/ImageFlow/GuFeng.json"]
    CompyPath = "ws://127.0.0.1:8188/ws"
    CompyPromptUrl = "http://127.0.0.1:8188/"
    ImagePath = "/article/image/"
    height = 720
    width = 480
    style: dict[str, str] = {"0": "GuFeng"}
    src_language = "Chinese"
    music_dict: dict[int, str | None] = {
        0: "/article/bgm/common",
        1: "/article/bgm/sad",
        2: "/article/bgm/common",
        3: "/article/bgm/happy",
        4: "article/bgm/success",
    }
    apikey_deepseek = "sk-4RA02El8XSHwNCQJ2471085cBd97445eB56075DaD82a567d"

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "algernon")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

    Ai_Video_DataBase = VideoDBManager(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        db=os.getenv("MYSQL_DB_AI", "video_db"),
    )
    Direct_Video_DataBase = VideoDBManager(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        db=os.getenv("MYSQL_DB_DIRECT", "video_db_2"),
    )
