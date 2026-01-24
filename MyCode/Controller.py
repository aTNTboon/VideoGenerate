from typing import Dict, Optional, TypedDict
import flask
import json
import os
import MyCode.SumService
import asyncio
from datetime import date
import os
from MyCode.Setting import Setting
from MyCode.BaseService import BaseService
from MyCode.util.Audio_requestUtil.Edge_TTS_Util import Edge_TTS_Util
from MyCode.util.Audio_requestUtil.Base_Audio_Util import Base_Audio_Util
from MyCode.util.Image_Generate_Util.Base_Image_Generate_Util import Base_Image_Generate_Util
from MyCode.util.Image_Generate_Util.Local_Image_WorkFlow import Local_Image_WorkFlow
from MyCode.util.Subtitle_Util.Whisper_Sybtitle import Whisper_Sybtitle_Util
from MyCode.util.Subtitle_Util.Base_Subtitle_Util import Base_Subtitle_Util
from MyCode.util.self_requestUtil.RequestAI import RequestAI
from MyCode.util.self_requestUtil.Base_Request import Base_Request
from MyCode.util.SceneParser import self_parse
from enum import Enum
import MyCode.util.Video_Edit_Util.VideoComposer as VideoComposer
import MyCode.util.Image_Generate_Util.GetPathFromPrompt_ID as GetPathFromPrompt_ID
from MyCode.util.Music_Chioce_Util.Music_Util import Music_Util
import time
app = flask.Flask(__name__)

class R(TypedDict):
    code: int
    msg: str
    data: Dict[str, str | int]



def extract_basic_response(response: R) -> Dict[str, str | int]:
    # 方法1：直接取值（存在KeyError风险，不推荐）
    # code = response['code']
    # 方法2：get方法（推荐，安全，支持默认值）

    code: int = response.get('code', 0)
    msg: str = response.get('msg', '未知消息')
    if(code!=200):
        raise Exception(f'无法接受{code}__{msg}')  # 不存在返回默认值0
    data: Dict[str, str | int] = response.get('data', {})
    return data

def create_baisc_response(code:int,msg:str,data:Dict[str, str | int])->R:
    """
    创建符合R类型的响应字典
    :param code: 状态码（整数）
    :param msg: 提示消息（字符串）
    :param data: 业务数据字典（键为字符串，值为字符串/整数）
    :return: 符合R类型的字典
    """
    # TypedDict本质是字典，直接返回符合结构的字典即可
    return {
        'code': code,
        'msg': msg,
        'data': data
    }

def create_wrng_response(msg):
    return{
        "code":401,
        "msg":msg,
        "data":{}
    }


@app.route('/message', methods=['POST'])
async def index():
    
    return "test"


if __name__ == "__init__":
    app.run()



