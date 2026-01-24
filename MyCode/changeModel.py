import os
from pathlib import Path
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion_inpaint import StableDiffusionInpaintPipeline
from diffusers.utils import logging

logging.set_verbosity_error()  # 关闭冗余日志

# -----------------------
# 路径配置
# -----------------------
ckpt_path = Path("/comfyUIProject/ComfyUI/models/checkpoints/sd-v1-5-inpainting.ckpt")
diffusers_path = Path("/article/MyCode/workflows/model")

# 创建目录
diffusers_path.mkdir(parents=True, exist_ok=True)

# -----------------------
# 转换函数
# -----------------------
def convert_ckpt_to_diffusers(ckpt_path: Path, diffusers_path: Path):
    """
    将 sd-1.5 inpainting ckpt 转换为 diffusers 格式
    """
    print(f"Converting ckpt: {ckpt_path} → {diffusers_path} ...")

    try:
        # 正确方法：from_single_file
        pipe = StableDiffusionInpaintPipeline.from_single_file(
            str(ckpt_path),
        )
    except Exception as e:
        print("❌ Error loading ckpt:", e)
        return

    # 保存为 diffusers 格式
    pipe.save_pretrained(str(diffusers_path))
    print("✅ Conversion done!")

# -----------------------
# 执行转换
# -----------------------
convert_ckpt_to_diffusers(ckpt_path, diffusers_path)
