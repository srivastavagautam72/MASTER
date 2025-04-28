import os

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from PIL import Image

app = Flask(__name__)
app.secret_key = os.getenv("secret_key")


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    """
    Check if the given filename is allowed based on the allowed extensions.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the filename has an allowed extension, False otherwise.
    """
    return filename.lower().endswith(tuple(ALLOWED_EXTENSIONS))


def is_valid_image(file):
    """
    Check if the given file is a valid image.

    Args:
        file: The file to check.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    return file and allowed_file(file.filename) if file else False


def compress_image(input_path, output_path, quality=85):
    """
    Compress the image located at the input path and save it to the output path with the specified quality.

    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to save the compressed image file.
        quality (int, optional): The quality of the compressed image. Defaults to 85.

    Returns:
        bool or str: True if the image is successfully compressed and saved, or an error message if an exception occurs.
    """
    try:
        with Image.open(input_path) as img:
            img.save(output_path, optimize=True, quality=quality)
        return True
    except Exception as e:
        return str(e)


@app.route("/", methods=["GET", "POST"])
def photo_compressor():
    """
    Handle the photo compressor route.

    If a POST request is received, the uploaded file is checked for validity and compressed if valid.
    The compressed file is then saved and the user is redirected to download it.
    If an error occurs during compression, an error message is flashed.

    Returns:
        Response: The rendered template for the index.html page.
    """
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":
            _, file_extension = os.path.splitext(uploaded_file.filename)
            if not is_valid_image(file_extension):
                return (
                    "Invalid file format. Please upload a valid image.",
                    400,
                )  # Return a 400 status code

            input_path = os.path.abspath(os.path.join("uploads", uploaded_file.filename))
            output_path = os.path.abspath(os.path.join("compressed", uploaded_file.filename))
            uploaded_file.save(input_path)

            compression_result = compress_image(input_path, output_path)
            if compression_result is True:
                return redirect(url_for("download_compressed", filename=uploaded_file.filename))
            else:
                flash(f"Compression Error: {compression_result}", "error")

    return render_template("index.html")


@app.route("/download/<filename>")
def download_compressed(filename):
    """
    Download the compressed file with the specified filename.

    Args:
        filename (str): The name of the compressed file to download.

    Returns:
        Response: The compressed file as an attachment for download.
    """
    compressed_path = os.path.join("compressed", filename)
    return send_file(compressed_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
