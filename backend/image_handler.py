# image_hendler.py

import os
from io import BytesIO

from PIL import Image
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_image(img, target_size=(300, 300)):
    img.thumbnail(target_size)
    return img


def compress_image(img, target_size_kb=5):
    quality = 95
    output = BytesIO()

    while True:
        img.save(output, format="JPEG", quality=quality)
        size_kb = len(output.getvalue()) / 1024

        if size_kb <= target_size_kb or quality <= 10:
            break

        quality -= 5
        output = BytesIO()

    return img, quality


def process_image(file):
    img = Image.open(file)
    img = resize_image(img)
    img, quality = compress_image(img)
    return img, quality


def handle_uploaded_file(file, upload_folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        img, quality = process_image(file)

        # Save the processed image to a temporary file or database
        # temp_filename = f"temp_{filename}"
        # img.save(temp_filename, format="JPEG", quality=quality)

        # Save the processed image to the specified uploads folder
        img_path = os.path.join(upload_folder, filename)
        img.save(img_path, format="JPEG", quality=quality)

        # Return the stored path
        return filename

    return None


# not implemented in this api app as it returns json only
# Serve uploaded images
# @app.route("/static/images/<filename>")
# def serve_image(filename):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
