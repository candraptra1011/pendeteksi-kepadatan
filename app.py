from flask import Flask, render_template, request, redirect
import os

from detector import process_video

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["video"]

    if file.filename == "":
        return redirect("/")

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    hasil = process_video(filepath)

    return render_template(
        "result.html",
        hasil=hasil
    )


if __name__ == "__main__":

    app.run(debug=True)