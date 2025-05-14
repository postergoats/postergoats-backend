import os
import uuid
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import asyncio

# Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# PosterGoat watermark (adjust as needed)
WATERMARK_PATH = "postergoats_watermark.png"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === 1. GPT-4o Enhanced Prompt ===
async def enhance_prompt(user_prompt):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Convert this into a vivid, descriptive art prompt for a high-quality poster, 24x36 inch format, photoreal or stylized, suitable for printing."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# === 2. DALL·E Image Generation ===
async def generate_image(prompt):
    dalle_response = await openai.Image.acreate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1536",  # Tall aspect for poster, original generation
        quality="hd",
        response_format="b64_json"
    )
    image_data = base64.b64decode(dalle_response["data"][0]["b64_json"])
    return Image.open(io.BytesIO(image_data))

# === 3. Apply Watermark ===
def apply_watermark(img: Image.Image) -> Image.Image:
    watermark = Image.open(WATERMARK_PATH).convert("RGBA")
    img = img.convert("RGBA")

    # Resize watermark
    scale = 0.12
    wm_width = int(img.width * scale)
    watermark = watermark.resize((wm_width, int(watermark.height * (wm_width / watermark.width))))

    # Position watermark in bottom-right
    padding = 40
    position = (img.width - watermark.width - padding, img.height - watermark.height - padding)
    img.alpha_composite(watermark, position)
    return img.convert("RGB")

# === 4. Resize and Save as 300DPI Poster ===
def save_300dpi_image(img: Image.Image, filename: str) -> str:
    dpi_output_size = (7200, 10800)  # 24x36 inches at 300 DPI
    img_resized = img.resize(dpi_output_size, Image.LANCZOS)
    full_path = os.path.join(OUTPUT_DIR, filename)
    img_resized.save(full_path, format="PNG", dpi=(300, 300))
    return full_path

# === 5. Main Entry Point for Poster Generation ===
async def generate_poster(prompt, upload_file=None, ai_reimagine=False):
    # Step 1: Enhance prompt
    final_prompt = await enhance_prompt(prompt)

    # Step 2: If image uploaded and ai_reimagine is true, skip (for now, basic only)
    if upload_file and ai_reimagine:
        raise NotImplementedError("Reimagine with upload not yet implemented.")
    elif upload_file:
        # Just return uploaded image without AI
        input_img = Image.open(upload_file.file)
    else:
        # Generate from prompt
        input_img = await generate_image(final_prompt)

    # Step 3: Save original poster
    original_filename = f"{uuid.uuid4()}_original.png"
    original_path = save_300dpi_image(input_img, original_filename)

    # Step 4: Apply watermark
    watermarked_img = apply_watermark(input_img)
    watermarked_filename = f"{uuid.uuid4()}_wm.png"
    watermarked_path = save_300dpi_image(watermarked_img, watermarked_filename)

    return original_path, watermarked_path
