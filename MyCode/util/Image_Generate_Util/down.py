#!/usr/bin/env python3
import os
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

# ---------- 配置 ----------
PROXY = "http://172.23.0.1:7897"
os.environ["HTTP_PROXY"] = PROXY
os.environ["HTTPS_PROXY"] = PROXY

MODEL_REPO = "runwayml/stable-diffusion-inpainting"
CACHE_DIR = Path("./cache_model")
CACHE_DIR.mkdir(exist_ok=True)

# 想要的主要文件
WANTED_FILES = [
    "model_index.json",
    "unet/diffusion_pytorch_model.bin",
    "vae/diffusion_pytorch_model.bin",
    "text_encoder/pytorch_model.bin",
    "tokenizer_config.json",
    "vocab.json",
    "scheduler_config.json",
    "safety_checker/pytorch_model.bin",  # 可选
]

# ---------- 获取远程 repo 文件 ----------
api = HfApi()
try:
    remote_files = api.list_repo_files(MODEL_REPO)
except Exception as e:
    print("⚠️ 无法获取 repo 文件列表，请检查网络/代理/模型名")
    raise e

# ---------- 下载缺失文件 ----------
for file in WANTED_FILES:
    local_path = CACHE_DIR / file
    if local_path.exists():
        print(f"✅ 已存在，跳过: {file}")
        continue
    if file not in remote_files:
        print(f"⚠️ 远程不存在，跳过: {file}")
        continue

    print(f"⬇️ 下载缺失文件: {file}")
    hf_hub_download(
        repo_id=MODEL_REPO,
        filename=file,
        cache_dir=str(CACHE_DIR),
        resume_download=True,   # 支持断点续传
    )

print("✔️ 检查并下载完成，所有缺失文件已补齐")
