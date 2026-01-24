# ==== 必须导入 ====
from diffusers.models.unets.unet_2d_condition import UNet2DConditionModel
from diffusers.models.autoencoders.autoencoder_kl import AutoencoderKL
from diffusers.schedulers.scheduling_ddim import DDIMScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from safetensors.torch import load_file

import torch
from tqdm.auto import tqdm
from PIL import Image
import numpy as np
from transformers import CLIPTextModel, CLIPTokenizer

import torch
from tqdm.auto import tqdm
from PIL import Image
import numpy as np

# ==== GPU 设置 ====
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16  # 半精度节省显存
print(f"Using device: {device}, dtype={torch_dtype}")

# ==== 清理显存 ====
torch.cuda.empty_cache()

# ==== 加载模型（网络下载 Hugging Face） ====
# Stable Diffusion v1.5
model_id = "runwayml/stable-diffusion-v1-5"

# UNet
unet = UNet2DConditionModel.from_pretrained(model_id, subfolder="unet", torch_dtype=torch_dtype).to(device)
unet.set_attention_slice("auto")  # attention slicing，节省显存

# VAE
vae = AutoencoderKL.from_pretrained(model_id, subfolder="vae", torch_dtype=torch_dtype).to(device)

# Tokenizer & TextEncoder
tokenizer = CLIPTokenizer.from_pretrained(model_id, subfolder="tokenizer")
text_encoder = CLIPTextModel.from_pretrained(model_id, subfolder="text_encoder", torch_dtype=torch_dtype).to(device)

# Scheduler
scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")
num_inference_steps = 15
scheduler.set_timesteps(num_inference_steps)

# ==== 文本编码 ====
prompt = "a simple flat illustration of a robot"
text_inputs = tokenizer([prompt], padding="max_length", max_length=77, return_tensors="pt")
text_embeddings = text_encoder(text_inputs.input_ids.to(device)).last_hidden_state

# ==== 初始 latent（512x512，batch=1） ====
height, width = 512, 512
latent = torch.randn((1, unet.in_channels, height//8, width//8), device=device, dtype=torch_dtype)

# ==== 多步采样 + tqdm 进度条 ====
progress_bar = tqdm(range(num_inference_steps), desc="Generating image")
for t in scheduler.timesteps:
    with torch.no_grad():
        noise_pred = unet(latent, t, encoder_hidden_states=text_embeddings).sample
        latent = scheduler.step(noise_pred, t, latent).prev_sample
    progress_bar.update(1)
progress_bar.close()

# ==== 解码 latent → 图像 ====
with torch.no_grad():
    image = vae.decode(latent / 0.18215).sample

# ==== 转为 PIL 并保存 ====
image = (image / 2 + 0.5).clamp(0, 1)
image = image.cpu().permute(0, 2, 3, 1).numpy()
image = (image * 255).round().astype(np.uint8)
pil_image = Image.fromarray(image[0])
pil_image.save("out.png")
print("Image saved as out.png")

