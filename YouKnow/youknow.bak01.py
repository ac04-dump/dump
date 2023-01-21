#!/usr/bin/env python3

from bs4 import BeautifulSoup
from gtts import gTTS
import os
import re
import requests
import sys
import random

RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"
TEMP_SPEECH_FILE = "/tmp/speech.mp3"
TEMP_IMAGES_FOLDER = "/tmp/images"

def error(msg: str) -> None:
    print("ERROR: " + msg)
    sys.exit(1)

def generate_speech(content: BeautifulSoup) -> str:
    paragraphs = content.find_all("p")
    text = ""
    for paragraph in paragraphs:
        if paragraph.text.strip() == "":
            continue
        pt = re.sub("\\[([1-9][0-9]?)\\]", "", paragraph.text.strip())
        if "You can help Wikipedia by expanding it." in pt:
            continue
        if text == "":
            text = pt
            continue
        text += "\n" + pt
    if text.strip() == "":
        error("no text found")
    #tts = gTTS(text=text, lang="en", slow=False)
    #tts.save(TEMP_SPEECH_FILE)
    return text

def get_images(content: BeautifulSoup, min_number: int) -> list:
    if os.path.exists(TEMP_IMAGES_FOLDER):
        for i in os.listdir(TEMP_IMAGES_FOLDER):
            os.remove(os.path.join(TEMP_IMAGES_FOLDER, i))
        os.rmdir(TEMP_IMAGES_FOLDER)
    os.mkdir(TEMP_IMAGES_FOLDER)
    imgs_all = content.find_all("img")
    imgs = []
    score = 0
    for i in imgs_all:
        if not i["src"].startswith("//upload.wikimedia.org/wikipedia"):
            continue
        if i["src"].strip().endswith("-Red_pog.svg.png"):
            continue
        if i["src"].endswith(".svg.png"):
            parts = i["src"].split("/")
            parts[-1] = re.sub("([1-9][0-9]?)px", "100px", parts[-1])
            imgs.append("https:" + "/".join(parts))
            score += 0.2
            continue
        imgs.append("https:" + i["src"])
        score += 1
    print(f"{score}/{min_number}")
    if score < min_number:
        error("too few images")
    files = []
    for i in imgs:
        print(i)
        r = requests.get(i, stream=True, headers={"Host": "upload.wikimedia.org", "Referer": "https://en.wikipedia.org/", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"})
        if r.status_code != 200:
            print("cannot download image" + str(r.status_code))
            continue
        fname = r.url.split("/")[-1]
        with open(os.path.join(TEMP_IMAGES_FOLDER, fname), 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        files.append(os.path.join(TEMP_IMAGES_FOLDER, fname))
    return files

def get_title(content: BeautifulSoup) -> str:
    t = content.find(id="firstHeading")
    if t is None:
        error("no heading found")
    return t.text

if __name__ == "__main__":
    r = requests.get(RANDOM_ARTICLE_URL)
    if r.status_code != 200:
        error("got error response from wikipedia")
    url = r.url

    if url.startswith("https://en.wikipedia.org/wiki/List_of_"):
        error("list article")

    soup = BeautifulSoup(r.text, "html.parser")

    title = get_title(soup)
    text = generate_speech(soup)
    min_imgs_number = len(text) / 700
    if min_imgs_number > 10: min_imgs_number = 10
    images = get_images(soup, min_imgs_number)

    print(url)
    print(title)
    print(text)

    #os.system(f"mpv --speed=1.3 {TEMP_SPEECH_FILE}")

