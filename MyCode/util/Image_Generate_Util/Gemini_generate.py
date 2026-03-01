# import os
# import uuid
# import base64
# from typing import Dict, List
# from google import genai

# def generate_anime_images(
#     prompts: Dict[int, List[str]],
#     output_dir: str = "./gemini_outputs",
#     image_quality: str = "4K 高清",
# ):


#     os.environ["GEMINI_API_KEY"] = "AIzaSyAYGp2M1AE_jfm_sYJfKms8jB0YyLoyuRQ"
#     """
#     Gemini 文生图版本（替代 SDXL）
#     """

#     client = genai.Client()

#     os.makedirs(output_dir, exist_ok=True)

#     # 读取角色 / 风格 prompt
#     extra = ""
#     with open("/article/MyCode/prompt/role.txt", "r", encoding="utf-8") as f:
#         extra = f.read()

#     negative_prompt = (
#         "不要出现：文字、水印、Logo、签名、模糊、畸形、变异、丑陋、"
#         "低分辨率、解剖错误、多余肢体、裁剪、画面不完整"
#     )

#     results: Dict[int, List[str]] = {}

#     for video_id, prompts_list in prompts.items():
#         results[video_id] = []

#         for i, prompt in enumerate(prompts_list):
#             print(f"Generating {video_id} - {i+1}/{len(prompts_list)}")

#             # Gemini 推荐：结构化关键词 + 语义
#             full_prompt = f"""
# 生成一张动漫风格插画：

# 主题描述：
# {prompt}

# 角色与风格设定：
# {extra}

# 画面要求：
# {image_quality}
# 动漫插画风格，细节丰富，线条干净，色彩统一

# 限制条件：
# {negative_prompt}
# """

#             response = client.models.generate_content(
#                 model="gemini-2.5-flash-image",
#                 contents=full_prompt,
#                 config={
#                     "response_modalities": ["IMAGE"]
#                 }
#             )

#             for part in response.candidates[0].content.parts:
#                 if part.inline_data:
#                     image_bytes = base64.b64decode(part.inline_data.data)
#                     save_path = os.path.join(
#                         output_dir, f"anime_{uuid.uuid4()}.png"
#                     )
#                     with open(save_path, "wb") as f:
#                         f.write(image_bytes)

#                     results[video_id].append(save_path)

#     return results


# if __name__ == "__main__":
#     # 构造测试 prompts
#     test_prompts = {
#         1: [
#             "一个穿着校服的动漫女孩，长发，站在樱花树下，春天",
#             "同一个女孩，在黄昏的街道上，微风，温暖色调"
#         ],
#         2: [
#             "银发动漫少年，黑色风衣，夜晚城市，赛博朋克风格"
#         ]
#     }

#     results = generate_anime_images(
#         prompts=test_prompts,
#         output_dir="./gemini_test_outputs",
#         image_quality="高清，动漫插画风格"
#     )

#     print("生成结果：")
#     for video_id, images in results.items():
#         print(f"Video {video_id}:")
#         for img_path in images:
#             print(f"  - {img_path}")
