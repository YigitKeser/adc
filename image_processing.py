import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
import webcolors

# Function to find the closest CSS3 color name for a given hex color
def closest_color(hex_color):
    min_colors = {}
    r, g, b = webcolors.hex_to_rgb(hex_color)

    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        rd, gd, bd = webcolors.hex_to_rgb(key)
        min_colors[(abs(r - rd) ** 2 + abs(g - gd) ** 2 + abs(b - bd) ** 2)] = name

    return min_colors[min(min_colors.keys())]

# Function to convert a hex color code to a CSS3 color name
def hex_to_color_name(hex_color):
    try:
        color_name = webcolors.hex_to_name(hex_color, spec='css3')
    except ValueError:
        try:
            color_name = closest_color(hex_color)
        except Exception:
            color_name = "unknown color"
    return color_name

# Function to generate an image based on a text prompt and a hex color code
def generate_image(image_path, text_prompt, hex_color):
    # Pretrained model identifier
    model_id = "CompVis/stable-diffusion-v1-4"
    # Check if CUDA is available and set the device accordingly
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Load the Stable Diffusion model
    img2img_model = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    img2img_model = img2img_model.to(device)

    # Load and resize the starting image
    start_image = Image.open(image_path).convert("RGB")
    start_image = start_image.resize((512, 512))

    # Find the closest CSS3 color name for the given hex color
    color_name = hex_to_color_name(hex_color)

    # Create a full prompt by combining the text prompt and color information
    full_prompt = f"{text_prompt}, using a noticeable amount of {color_name} color"

    # Set the strength for diffusion
    strength = 0.8

    # Generate a new image using the model and provided inputs
    with torch.no_grad():
        generated_image = img2img_model(
            prompt=full_prompt,
            image=start_image,
            strength=strength,
            num_inference_steps=50
        )["images"][0]

    return generated_image