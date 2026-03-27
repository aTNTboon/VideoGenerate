from typing import Any, Dict, TypedDict

import flask
from flask import request

from MyCode.sqlManager import VideoDBManager
from MyCode.video_creation import (
    DirectSubtitleRequest,
    MoviePyVideoEditor,
    PlainTextSubtitleProvider,
    VideoCreationService,
    copy_video_to_workspace,
    persist_uploaded_subtitle,
    persist_uploaded_video,
)
from MyCode.video_repository import SqlVideoRepository
from MyCode.video_service import VideoQueryService


class R(TypedDict):
    code: int
    msg: str
    data: Dict[str, Any]


def create_basic_response(code: int, msg: str, data: Dict[str, Any]) -> R:
    return {"code": code, "msg": msg, "data": data}


def create_success_response(data: Dict[str, Any]) -> R:
    return {"code": 200, "msg": "", "data": data}


def build_dependencies() -> tuple[SqlVideoRepository, VideoQueryService, VideoCreationService]:
    db = VideoDBManager(host="localhost", user="algernon", password="123", db="video_db")
    repo = SqlVideoRepository(db)
    video_service = VideoQueryService(repo)
    creation_service = VideoCreationService(
        subtitle_provider=PlainTextSubtitleProvider(), video_editor=MoviePyVideoEditor()
    )
    return repo, video_service, creation_service


app = flask.Flask(__name__)
repo, video_service, creation_service = build_dependencies()


@app.route("/getStep/<step>", methods=["GET"])
def getStep(step) -> R:
    try:
        step_int = int(step)
        video_data = video_service.get_videos_by_step(step_int)
        return create_success_response(data={"videoList": video_data})
    except ValueError:
        return create_basic_response(
            data={"error": "step参数必须是整数"}, code=400, msg="参数错误"
        )
    except Exception as e:
        return create_basic_response(
            data={"error": f"获取视频列表失败：{str(e)}"},
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

    if filters["theme"] is not None:
        filters["theme"] = int(filters["theme"])  # type: ignore
    if filters["mood"] is not None:
        filters["mood"] = int(filters["mood"])  # type: ignore
    if filters["step"] is not None:
        filters["step"] = int(filters["step"])  # type: ignore

    data = video_service.query_videos(filters)
    return create_success_response(data={"videoList": data})


@app.route("/getByName/<name>", methods=["GET"])
def getByName(name):
    data = video_service.query_videos_by_name(name)
    return create_success_response(data={"videoList": data})


@app.route("/deleteId/<id>", methods=["POST"])
def deletefromId(id):
    repo.delete_video_by_id(int(id))
    return create_basic_response(code=200, msg="删除成功", data={})


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
        new_id = repo.insert_finished_video(vid, text, mood, path)
        return create_success_response(data={"id": new_id})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo", methods=["GET"])
def list_finished_videos():
    filters: Dict[str, Any] = {}
    for key in ("id", "video_id", "text", "mood", "videoPath"):
        v = request.args.get(key)
        if v is not None:
            filters[key] = v
    try:
        rows = repo.query_finished_videos(**filters)
        return create_success_response(data={"rows": rows})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo/<int:fid>", methods=["PUT"])
def update_finished_video(fid):
    try:
        payload = request.get_json(force=True)
        count = repo.update_finished_video(
            fid,
            video_id=payload.get("video_id"),
            text=payload.get("text"),
            mood=payload.get("mood"),
            videoPath=payload.get("videoPath"),
        )
        return create_success_response(data={"updated": count})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/finishedVideo/<int:fid>", methods=["DELETE"])
def delete_finished_video(fid):
    try:
        cnt = repo.delete_finished_video(fid)
        return create_success_response(data={"deleted": cnt})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/video/addSubtitle", methods=["POST"])
def add_subtitle_to_video():
    """Support direct video upload/path + subtitle text/file, then generate subtitled video."""
    try:
        video_path = request.form.get("video_path")
        video_file = request.files.get("video")
        subtitle_file = request.files.get("subtitle")
        subtitle_text = request.form.get("subtitle_text")
        output_path = request.form.get("output_path")

        if video_file:
            video_path = persist_uploaded_video(video_file)
        elif video_path:
            video_path = copy_video_to_workspace(video_path)

        if not video_path:
            return create_basic_response(400, "必须提供 video 文件或 video_path", {})

        subtitle_path = None
        if subtitle_file:
            subtitle_path = persist_uploaded_subtitle(subtitle_file)

        request_dto = DirectSubtitleRequest(
            video_path=video_path,
            subtitle_text=subtitle_text,
            subtitle_path=subtitle_path,
            output_path=output_path,
        )
        result_path = creation_service.add_subtitle_to_direct_video(request_dto)
        return create_success_response(data={"videoPath": result_path})
    except Exception as e:
        return create_basic_response(code=500, msg=str(e), data={})


@app.route("/file/<path:filename>", methods=["GET"])
def file_detail(filename):
    if str(filename).startswith("article"):
        filename = "/" + filename

    return flask.send_file(
        filename,
        mimetype="video/mp4",
        as_attachment=False,
        conditional=True,
    )


if __name__ == "__main__":
    app.run()
