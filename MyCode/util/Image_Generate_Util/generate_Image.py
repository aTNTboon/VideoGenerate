import os
import time
import uuid
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis, MultiModalConversation
import dashscope
from typing import Dict, List

from MyCode.Setting import Setting

# set base URL for dashscope (Beijing region by default)
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"


def remote_generate_anime_images(
    prompts: Dict[int, str],
    output_dir: str = "./sd_outputs",
    size: str = "1664*928",
    model: str = "qwen-image-max",
    api_key: str | None = None,
) -> Dict[int, str]:
    """Use Aliyun Dashscope API to synthesise images for given prompts.

    The `prompts` argument should be a mapping from an arbitrary key (e.g. video
    id) to a list of prompt strings.  Each generated image is downloaded and
    saved locally under ``output_dir`` using a uuid+timestamp name; the function
    returns a mapping with the same keys whose values are lists of save paths.

    ``api_key`` may be passed directly or will be read from the
    ``DASHSCOPE_API_KEY`` environment variable.
    """
    extra = ""
    with open("/article/MyCode/prompt/role.txt") as f:
        extra = f.read()
    style = ""
    with open("/article/MyCode/prompt/style.txt") as f1:
        style = f1.read()
    results: Dict[int, str] = {}

    for vid, prompt in prompts.items():
        results[vid] = ""
        messages = [{"role": "user", "content": [{"text": style + extra + prompt}]}]
        print(f"calling dashscope for prompt: {prompt}")
        max_retries = 1000
        rsp = None
        for attempt in range(max_retries):
            try:
                rsp = MultiModalConversation.call(
                    api_key=Setting.image_api,
                    model="qwen-image-max",
                    messages=messages,
                    result_format="message",
                    stream=False,
                    watermark=False,
                    prompt_extend=True,
                    negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。",
                    size="1664*928",
                )
            except Exception as exc:
                print(f"dashscope call raised exception: {exc}")
                if attempt < max_retries - 1:
                    print("retrying after 10s...")
                    time.sleep(10)
                    continue
                else:
                    rsp = None
                    break

            status = getattr(rsp, "status_code", None)
            if status == 200:
                break
            else:
                print(
                    f"dashscope call failed: status={status} code={getattr(rsp, 'code', '')} msg={getattr(rsp, 'message', '')}"
                )
                if attempt < max_retries - 1:
                    print("retrying after 10s...")
                    time.sleep(10)
                    continue
                else:
                    break

        if not rsp or getattr(rsp, "status_code", None) != 200:
            # give up on this prompt after retries
            continue

        # some responses use output.results, others embed in choices/message/content
        images = []
        out = getattr(rsp, "output", {})

        # try dict-style access first to avoid KeyError
        if isinstance(out, dict):
            for o in out.get("results", []):
                if isinstance(o, dict) and o.get("url"):
                    images.append(o["url"])
        else:
            # object with attributes
            if hasattr(out, "results") and out.results:
                for o in out.results:
                    url = getattr(o, "url", None)
                    if url:
                        images.append(url)

        # if still empty, attempt new-style payload with choices
        if not images:
            try:
                choices = (
                    out.get("choices")
                    if isinstance(out, dict)
                    else getattr(out, "choices", None)
                )
                if choices:
                    for choice in choices:
                        msg = choice.get("message", {})
                        content_list = msg.get("content", [])
                        for c in content_list:
                            if isinstance(c, dict) and "image" in c:
                                images.append(c["image"])
            except Exception:
                pass

        for url in images:
            file_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(
                output_dir, f"anime_{uuid.uuid4()}_{time.time()}_{file_name}"
            )
            try:
                resp_img = requests.get(url)
                resp_img.raise_for_status()
                with open(save_path, "wb+") as f:
                    f.write(resp_img.content)
                results[vid] = save_path
            except Exception as e:
                print(f"failed to download image {url}: {e}")
    return results


if __name__ == "__main__":
    # quick sanity check
    prompts = {
        0: "Silver-haired Lin Yan standing among crowd, focused gaze directed at the distant man and his glowing wolf on the platform during sunset"
    }
    out = remote_generate_anime_images(prompts)
    print("generated", out)
