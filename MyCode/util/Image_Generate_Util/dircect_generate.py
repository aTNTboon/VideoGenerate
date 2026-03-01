import os
import time
from typing import Dict
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler  # type: ignore

# import os
import gc

# os.environ["HTTP_PROXY"] = "http://172.23.0.1:7897"
# os.environ["HTTPS_PROXY"] = "http://172.23.0.1:7897"
# os.environ["ALL_PROXY"] = "socks5://172.23.0.1:7897"  # 如果是 socks5
import uuid


def generate_anime_images(
    prompts: Dict[int, str],
    output_dir: str = "./sd_outputs",
    width: int = 1080,
    height: int = 720,
    steps: int = 20,
    guidance_scale: float = 8.0,
):
    pipe = StableDiffusionXLPipeline.from_pretrained(
        # "/article/waiIllustriousSDXL_diffusers",
        "cagliostrolab/animagine-xl-4.0",
        torch_dtype=torch.float16,
        local_files_only=False,
        device="cuda",
        low_cpu_mem_usage=True,  # 只在加载阶段就优化内存
    )
    pipe.enable_vae_tiling()
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    # .to(device)
    extra = ""
    with open("/article/MyCode/prompt/role.txt") as f:
        extra = f.read()
    style = ""
    with open("/article/MyCode/prompt/style.txt") as f1:
        style = f1.read()
    try:
        pipe.load_lora_weights(
            "/article/ZZZlora/test.safetensors"
        )  # Replace with actual path to LoRA weights
        pipe.fuse_lora(lora_scale=1)
    except Exception as e:
        print(f"Error loading LoRA weights: {e}")
    # 优化显存
    # if hasattr(pipe, "enable_model_cpu_offload"):
    #     pipe.enable_model_cpu_offload()  # 非必要权重放到 CPU
    if hasattr(pipe, "enable_xformers_memory_efficient_attention"):
        pipe.enable_xformers_memory_efficient_attention()  # 更高效注意力
    results: Dict[int, str] = {}
    with torch.no_grad():
        for video_id in prompts.keys():
            prompt = prompts[video_id]
            os.makedirs(output_dir, exist_ok=True)
            results[video_id] = ""
            image = pipe(
                prompt=style + "," + prompt + "," + extra,
                negative_prompt="bad quality,worst quality,worst detail,sketch,censor,\
                    text, blurry, deformed, mutated, ugly, lowres, bad anatomy, extra limbs, cropped, poorly drawn",
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=None,
            ).images[0]  # type: ignore
            save_path = os.path.join(
                output_dir, f"anime_{uuid.uuid4()}_{time.time()}.png"
            )
            image.save(save_path)
            results[video_id] = save_path
    del pipe  # 删除 Python 对象引用
    torch.cuda.empty_cache()  # 清理 GPU 显存
    gc.collect()  # 回收 Python 内存
    return results


if __name__ == "__main__":
    prompt_list = ["cute comic", "cute cat"]
    map = {}
    map["test"] = prompt_list
    paths = generate_anime_images(
        prompts=map,
        output_dir="./sd_outputs",
        width=720,
        height=480,
        steps=20,
        guidance_scale=7.5,
    )

    print("Saved images:", paths)
