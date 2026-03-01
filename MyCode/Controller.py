
from typing import Any, Dict, List, TypedDict
import flask
import pytest
from MyCode.sqlManager import VideoDBManager
from MyCode.entity.VideoEntity import VideoEntity
from flask import request

app = flask.Flask(__name__)
db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")


class R(TypedDict):
    code: int
    msg: str
    data: Dict[str, Any]


def extract_basic_response(response: R) -> Dict[str, Any]:
    # 方法1：直接取值（存在KeyError风险，不推荐）
    # code = response['code']
    # 方法2：get方法（推荐，安全，支持默认值）

    code: int = response.get("code", 0)
    msg: str = response.get("msg", "未知消息")
    if code != 200:
        raise Exception(f"无法接受{code}__{msg}")  # 不存在返回默认值0
    data: Dict[str, Any] = response.get("data", {})
    return data


def create_basic_response(code: int, msg: str, data: Dict[str, Any]) -> R:
    return {"code": code, "msg": msg, "data": data}


def create_success_response(data: Dict[str, Any]) -> R:
    return {"code": 200, "msg": "", "data": data}


def create_wrong_response(msg) -> R:
    return {"code": 401, "msg": msg, "data": {}}


def transTurpleToData(data):
    videoList: List[VideoEntity] = []
    for video_dict in data:
        # 实例化VideoEntity
        video = VideoEntity()
        video.id = video_dict.get("id", "0")
        # 赋值所有13个字段（与videos表/insert_video方法完全对齐）
        video.video_id = video_dict.get("video_id", "")  # 视频ID
        video.uid = video_dict.get("uid", "")  # 用户ID
        video.theme = int(video_dict.get("theme", 0))  # 主题（转int，默认0）
        video.scene = video_dict.get("scene", "")  # 场景
        video.src_path = video_dict.get("src_path", "")  # 源文件路径
        video.audio_path = video_dict.get("audio_path", "")  # 音频路径
        video.mood = int(video_dict.get("mood", 0))  # 情绪（转int，默认0）
        video.music_path = video_dict.get("music_path", "")  # 音乐路径
        video.video_path = video_dict.get("video_path", "")  # 视频路径
        video.output_path = video_dict.get("output_path", "")  # 输出路径
        video.step = int(video_dict.get("step", 0))  # 步骤（转int，默认0）
        video.prompts = video_dict.get("prompts", "")  # 提示词
        video.text = video_dict.get(
            "text", "默认小说名"
        )  # 文本（默认值与insert_video一致）
        # 将赋值完成的实体添加到列表
        videoList.append(video)

    # 4. 转换为字典列表（前端可直接解析，依赖VideoEntity的to_dict方法）
    video_data: List[Dict[str, Any]] = [v.to_dict() for v in videoList]
    return video_data


# ___________________________________
# ___________________________________
# ___________________________________
# ___________________________________
# ___________________________________
# ___________________________________


@app.route("/getStep/<step>", methods=["GET"])
def getStep(step) -> R:
    try:
        # 1. 转换step为整数（数据库step字段是int类型，避免查询错误）
        step_int = int(step)

        # 2. 从数据库获取对应step的待处理视频列表
        # 假设db.get_pending_videos返回的是字典列表（每个字典对应一条视频数据）
        step_videos = db.get_pending_videos(step_int)
        # 3. 遍历数据，为VideoEntity赋值所有字段
        video_data = transTurpleToData(data=step_videos)
        return create_success_response(data={"videoList": video_data})

    except ValueError:
        # 处理step参数非数字的异常
        return create_basic_response(
            data={"error": "step参数必须是整数"}, code=400, msg="参数错误"
        )
    except Exception as e:
        # 捕获其他所有异常（如数据库查询失败）
        return create_basic_response(
            data={"error": f"获取视频列表失败：{str(e)}:{str(e.__traceback__)}"},
            code=500,
            msg="服务器内部错误",
        )


@app.route("/videos", methods=["GET"])
def query_videos():
    filters = {
        "uid": request.args.get("uid"),
        "theme": request.args.get("theme"),
        "mood": request.args.get("mood"),
        "step": request.args.get("step"),
        "name": request.args.get("name"),
    }

    # 类型转换
    if filters["theme"] is not None:
        filters["theme"] = int(filters["theme"])  # type: ignore
    if filters["mood"] is not None:
        filters["mood"] = int(filters["mood"])  # type: ignore
    if filters["step"] is not None:
        filters["step"] = int(filters["step"])  # type: ignore

    result = db.query_videos(filters)
    data = transTurpleToData(result)
    return create_success_response(data={"videoList": data})


@app.route("/getByName/<name>", methods=["GET"])
def getByName(name):
    result = db.selectByText(name)
    data = transTurpleToData(data=result)
    return create_success_response(data={"videoList": data})


@app.route("/deleteId/<id>", methods=["POST"])
def deletefromId(id):
    db.delete_from_id(id, "videos")
    return create_basic_response(code=200, msg="删除成功", data={})


# ------------------------------------------------
# finishedVideo 通用 CRUD 接口
# ------------------------------------------------


@app.route("/finishedVideo", methods=["POST"])
def create_finished_video():
    try:
        payload = request.get_json(force=True)
        vid = payload.get("video_id")
        text = payload.get("text", "")
        mood = payload.get("mood", "")
        path = payload.get("videoPath", "")
        if vid is None:
            return create_basic_response(code=400, msg="缺少video_id", data={})
        new_id = db.insert_finished_video(vid, text, mood, path)
        return create_success_response(data={"id": new_id})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo", methods=["GET"])
def list_finished_videos():
    # 支持多种查询参数
    filters = {}
    for key in ("id", "video_id", "text", "mood", "videoPath"):
        v = request.args.get(key)
        if v is not None:
            filters[key] = v
    try:
        rows = db.query_finished_videos(**filters)
        # 转换为列表字典
        return create_success_response(data={"rows": rows})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo/<int:fid>", methods=["PUT"])
def update_finished_video(fid):
    try:
        payload = request.get_json(force=True)
        vid = payload.get("video_id")
        text = payload.get("text")
        mood = payload.get("mood")
        path = payload.get("videoPath")
        count = db.update_finished_video(
            fid, video_id=vid, text=text, mood=mood, videoPath=path
        )
        return create_success_response(data={"updated": count})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo/<int:fid>", methods=["DELETE"])
def delete_finished_video(fid):
    try:
        cnt = db.delete_finished_video(fid)
        return create_success_response(data={"deleted": cnt})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


# __________________________________________________________________
# __________________________________________________________________
# __________________________________________________________________
# __________________________________________________________________
# __________________________________________________________________
@app.route("/file/<path:filename>", methods=["GET"])
def file_detail(filename):
    if str(filename).startswith("article"):
        filename = "/" + filename

    return flask.send_file(
        filename,
        mimetype="video/mp4",  # 根据你的视频格式调整（如video/avi、video/mov）
        as_attachment=False,  # 不下载，直接在客户端播放
        conditional=True,  # 支持断点续传，优化大视频加载
    )


if __name__ == "__init__":
    app.run()





@pytest.mark.parametrize(
    "url,expected_code",
    [
        ("/getStep/1", 200),
        ("/getStep/abc", 400),
        ("/getStep/-1", 200),
    ],
)
def test_get_step_batch(client, mocker, url, expected_code):
    mock_db = mocker.patch("app.db")
    mock_db.get_pending_videos.return_value = []

    response = client.get(url)
    json_data = response.get_json()

    assert json_data["code"] == expected_code
