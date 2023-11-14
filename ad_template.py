from PIL import Image, ImageDraw, ImageFont
from image_processing import hex_to_color_name

def create_ad_template(base_image_path, logo_path, punchline_and_button_color_hex, punchline_text, button_text):
    # Open the base image and logo image, and convert them to RGBA format
    base_image = Image.open(base_image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Get the width and height of the base image
    base_width, base_height = base_image.size

    # Create a canvas with a height that allows space for the base image and logo
    canvas_height = base_height + base_height // 2
    canvas = Image.new("RGBA", (base_width, canvas_height), "white")

    # Paste the base image onto the canvas
    canvas.paste(base_image, (0, base_height // 5))

    # Resize and paste the logo onto the canvas
    logo_size = base_width // 6
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    logo_position = (base_width // 2 - logo_size // 2, 3)
    canvas.paste(logo, logo_position, logo)

    # Create fonts for punchline and button text, or use defaults if the fonts are not found
    try:
        punchline_font = ImageFont.truetype("arial.ttf", size=base_height // 20)
        button_font = ImageFont.truetype("arial.ttf", size=base_height // 25)
    except IOError:
        punchline_font = ImageFont.load_default()
        button_font = ImageFont.load_default()

    # Create a drawing context on the canvas
    draw = ImageDraw.Draw(canvas)

    # Calculate positions for punchline and button text
    punchline_position = (base_width // 2, canvas_height - base_height // 5)
    button_position = (base_width // 2, canvas_height - base_height // 10)

    # Calculate the size and position of the button rectangle
    button_size = draw.textsize(button_text, font=button_font)
    button_rectangle = [(button_position[0] - button_size[0] // 2 - 20, button_position[1] - button_size[1] // 2 - 10),
                        (button_position[0] + button_size[0] // 2 + 20, button_position[1] + button_size[1] // 2 + 10)]

    # Draw the button rectangle and text on the canvas
    draw.rectangle(button_rectangle, fill=hex_to_color_name(punchline_and_button_color_hex))
    draw.text(button_position, button_text, font=button_font, fill="white", anchor="mm")

    # Draw the punchline text on the canvas with the specified color
    draw.text(punchline_position, punchline_text, font=punchline_font, fill=hex_to_color_name(punchline_and_button_color_hex), anchor="mm")

    return canvas
