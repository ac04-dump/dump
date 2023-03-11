#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import werkzeug.exceptions

TEMPDIR = "/home/alex/Temp"
PORT = 9999

app = Flask(__name__)

def get_hostname():
    with open("/etc/hostname") as f:
        return f.read()

@app.route("/")
def index():
    try:
        success_arg = request.args["success"]
    except werkzeug.exceptions.BadRequestKeyError:
        success_arg = None
    try:
        filename = request.args["name"]
    except werkzeug.exceptions.BadRequestKeyError:
        filename = None
    if success_arg == "true":
        heading = f"{filename} were uploaded successfully."
    else:
        heading = ""
    return render_template("index.html", hostname=get_hostname(), heading=heading)

@app.route("/upload", methods=["POST"])
def upload():
    if "upload" not in request.files:
        print("no files selected")
        return redirect("/")
    files = request.files.getlist("upload")
    for file in files:
        if file.filename is None:
            continue
        fname = secure_filename(file.filename)
        if "." not in fname:
            fname = fname + ".bin"
        fpath = f"{TEMPDIR}/{fname}"
        i = 0
        while os.path.exists(fpath):
            base = ".".join(fname.split(".")[:-1])
            ext = fname.split(".")[-1]
            i += 1
            fpath = f"{TEMPDIR}/{base}-{i}.{ext}"
        file.save(fpath)
    return redirect(f"/?success=true&name={[file.filename for file in files]}")

#app.run(port=PORT, debug=True, host="0.0.0.0")
app.run(port=PORT, host="0.0.0.0")

