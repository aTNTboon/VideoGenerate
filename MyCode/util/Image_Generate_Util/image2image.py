from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion_inpaint import StableDiffusionInpaintPipeline
from PIL import Image
import torch
import os

def getImage(prompt:str):
    PROXY = "http:/`/172.23.0.1:7897"
    os.environ.setdefault("HTTP_PROXY", PROXY)
    os.environ.setdefault("HTTPS_PROXY", PROXY)

    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",  # 这里直接用 repo
        torch_dtype=torch.float16
    ).to("cuda")

    pipe.enable_attention_slicing()
    pipe.vae.enable_slicing()

    # 全图生成示例（mask 全白 + 空白 init_image）
    w, h = 720,480
    init_image = Image.new("RGB", (w, h), (127, 127, 127))
    # init_image = Image.open("test.jpg").convert("RGB")
    mask = Image.new("L", (w, h), 255)  # 白色表示重绘
    generator = torch.Generator("cuda").manual_seed(42)

    out = pipe(
        prompt=prompt,
        image=init_image,
        mask_image=mask,
        height=h,
        width=w,
        num_inference_steps=20,
        guidance_scale=7.5,
        generator=generator,
    )

    out.images[0].save("inpaint_result.png")
