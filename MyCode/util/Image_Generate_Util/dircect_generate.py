import os
from typing import Dict
import torch
from diffusers import StableDiffusionXLPipeline
# import os
import gc

# os.environ["HTTP_PROXY"] = "http://172.23.0.1:7897"
# os.environ["HTTPS_PROXY"] = "http://172.23.0.1:7897"
# os.environ["ALL_PROXY"] = "socks5://172.23.0.1:7897"  # 如果是 socks5


def generate_anime_images(
    prompts: Dict[int, list[str]],
    output_dir: str = "./sd_outputs",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    guidance_scale: float = 7.5,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "/article/waiIllustriousSDXL_diffusers",
        torch_dtype=torch.float16,
        local_files_only=True,
        device_map="balanced",
        low_cpu_mem_usage=True  # 只在加载阶段就优化内存
    )
    # .to(device)


    # 优化显存
    # if hasattr(pipe, "enable_model_cpu_offload"):
    #     pipe.enable_model_cpu_offload()  # 非必要权重放到 CPU
    if hasattr(pipe, "enable_xformers_memory_efficient_attention"):
        pipe.enable_xformers_memory_efficient_attention()  # 更高效注意力
    results :Dict[int, list[str]]= {}
    for video_id in prompts.keys():
        prompts_list:list[str] = prompts[video_id]
        dirs=os.path.join(output_dir, str(video_id))
        os.makedirs(dirs, exist_ok=True)
        results[video_id]=[]
        for i, prompt in enumerate(prompts_list):
            print(f"Generating {i+1}/{len(prompts_list)}: {prompt}")
            image = pipe(
                prompt=prompt,
                negative_prompt="low quality, blurry, bad anatomy,nsfw",
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                ).images[0]
                
            save_path = os.path.join(dirs, f"anime_{i}.png")
            image.save(save_path)
            results[video_id].append(save_path)

            del image
            torch.cuda.empty_cache()
    return results



if __name__ == "__main__":
    prompt_list = [
        "anime style, handsome male student, cherry blossom campus, cinematic lighting, vibrant colors, soft glow, dreamy atmosphere"
    ]
    map={}
    map["test"]=prompt_list
    paths = generate_anime_images(
        prompts=map,
        output_dir="./sd_outputs",
        width=720,
        height=480,
        steps=20,
        guidance_scale=7.5,
    )

    print("Saved images:", paths)
