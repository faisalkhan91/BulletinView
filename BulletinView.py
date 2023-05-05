#!/bin/python3

from flask import Flask, render_template
from os import listdir


def get_images():
    main_dir = "assets/images"
    files = listdir(main_dir)
    images_list = [i for i in files if i.endswith('.jpg')]
    return images_list

app = Flask(__name__)
@app.route("/")
def index():
    get_image_list = get_images()
    return render_template("bulletin.html", pic=get_image_list)

app.run(host="0.0.0.0", port =80)