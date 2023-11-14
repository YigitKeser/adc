import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
import webcolors

def closest_color(hex_color):
    min_colors = {}
    r, g, b = webcolors.hex_to_rgb(hex_color)

    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        rd, gd, bd = webcolors.hex_to_rgb(key)
        min_colors[(abs(r - rd) ** 2 + abs(g - gd) ** 2 + abs(b - bd) ** 2)] = name

    return min_colors[min(min_colors.keys())]

def hex_to_color_name(hex_color):
    try:
        color_name = webcolors.hex_to_name(hex_color, spec='css3')
    except ValueError:
        try:
            color_name = closest_color(hex_color)
        except Exception:
            color_name = "unknown color"
    return color_name

def generate_image(image_path, text_prompt, hex_color):

    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    img2img_model = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    img2img_model = img2img_model.to(device)

    start_image = Image.open(image_path).convert("RGB")
    start_image = start_image.resize((512, 512))

    color_name = hex_to_color_name(hex_color)
    full_prompt = f"{text_prompt}, using noticable amount of {color_name} color"

    strength = 0.8 
    with torch.no_grad():
        generated_image = img2img_model(prompt=full_prompt
                                        #, guidance_scale=7
                                        , image=start_image
                                        , strength=strength
                                        , num_inference_steps=50)["images"][0]

    return generated_image
