import torch
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion_inpaint import StableDiffusionInpaintPipeline
import os

def generate_images_from_diffusers(
    prompts: list[str],
    output_dir: str = "./sd_outputs",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    guidance_scale: float = 7.5,
    seed: int | None = None,
    nsfw_filter: bool = True,
    device: str = "cuda"
):
    os.makedirs(output_dir, exist_ok=True)

    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    print("Loading diffusers model from Hugging Face...")
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        torch_dtype=torch.float16
    ).to(device)

    # 优化
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()

    # NSFW 检测
    if not nsfw_filter:
        pipe.safety_checker = None

    results = []

    for i, prompt in enumerate(prompts):
        print(f"Generating {i+1}/{len(prompts)}: {prompt}")

        # 如果没有 mask 或 init_image，就传 None
        image = pipe(
            prompt=prompt,
            image=None,
            mask_image=None,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]

        save_path = os.path.join(output_dir, f"image_{i}.png")
        image.save(save_path)
        results.append(save_path)

    return results


if __name__ == "__main__":
    prompt_list = [
        "a cinematic cyberpunk city at night",
        "a cute anime girl, pastel colors, soft lighting",
        "a realistic astronaut floating in space"
    ]

    paths = generate_images_from_diffusers(
        prompts=prompt_list,
        output_dir="./sd_outputs",
        width=768,
        height=768,
        steps=40,
        guidance_scale=8.0,
        seed=42,
        nsfw_filter=True
    )

    print("Saved images:", paths)
