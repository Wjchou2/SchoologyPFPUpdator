import os
import sys
import mimetypes
from datetime import datetime, time
import time;
import requests
from PIL import Image, ImageDraw, ImageFont


SIZE = 512
BG_COLOR = (20, 20, 20)
TEXT_COLOR = "white"


def load_font(size):
    """Try common macOS fonts, then fall back to default."""
    possible_fonts = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    for font_path in possible_fonts:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)

    print("Warning: could not find Helvetica/Arial, using default font.")
    return ImageFont.load_default()


def draw_centered(draw, canvas_size, text, font, y, fill=TEXT_COLOR):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    x = (canvas_size - width) / 2
    draw.text((x, y), text, fill=fill, font=font)


def generate_time_image(output_path="time.png"):
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    now = datetime.now()
    time_text = now.strftime("%-I:%M")
    ampm_text = now.strftime("%p")
    date_text = now.strftime("%b %d")

    time_font = load_font(135)
    small_font = load_font(45)

    draw_centered(draw, SIZE, time_text, time_font, 145)
    draw_centered(draw, SIZE, ampm_text, small_font, 285)
    draw_centered(draw, SIZE, date_text, small_font, 350)

    img.save(output_path)
    print(f"Generated image: {output_path}")
    return output_path


def upload_profile_picture(file_path):
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    user_id = os.getenv("SCHOOLOGY_USER_ID")
    csrf_key = os.getenv("SCHOOLOGY_CSRF_KEY")
    csrf_token = os.getenv("SCHOOLOGY_CSRF_TOKEN")
    cookie = os.getenv("SCHOOLOGY_COOKIE")

    if not all([user_id, csrf_key, csrf_token, cookie]):
        print("Missing environment variables.")
        print("Set these first:")
        print('  export SCHOOLOGY_USER_ID="YOUR_USER_ID"')
        print('  export SCHOOLOGY_CSRF_KEY="YOUR_CSRF_KEY"')
        print('  export SCHOOLOGY_CSRF_TOKEN="YOUR_CSRF_TOKEN"')
        print("  export SCHOOLOGY_COOKIE='YOUR_COOKIE_HEADER_VALUE'")
        sys.exit(1)

    url = f"https://schoology.shschools.org/profile_picture/upload/user/{user_id}/2"

    headers = {
        "X-CSRF-Key": csrf_key,
        "X-CSRF-Token": csrf_token,
        "Referer": f"https://schoology.shschools.org/user/{user_id}/info",
        "Cookie": cookie,
    }

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    data = {
        "name": filename,
        "chunk": "0",
        "chunks": "1",
        "use_plain": "1",
    }

    with open(file_path, "rb") as f:
        files = {
            "file": (filename, f, mime_type)
        }

        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=30,
        )

    print("Status:", response.status_code)
    print("Response:")
    print(response.text)

    if response.ok:
        print("Upload request succeeded.")
    else:
        print("Upload failed.")


def main():
    # If user gives a file path, upload that.
    # Otherwise, generate time.png and upload it.
    while True:

        if len(sys.argv) >= 2:
            file_path = sys.argv[1]
        else:
            file_path = generate_time_image("time.png")

        upload_profile_picture(file_path)
        # now = datetime.now()
        # seconds_until_next_minute = 60 - now.second - now.microsecond / 1_000_000

        # time.sleep(seconds_until_next_minute)



if __name__ == "__main__":
    main()