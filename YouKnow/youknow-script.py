#!/usr/bin/env python3

from bs4 import BeautifulSoup
from gtts import gTTS
import os
import random
import re
import requests
import sys
import subprocess

BACKGROUND_IMAGE = "/home/alex/_/youknow/bg.png"
OUTPUT_FILE = "/tmp/res.mkv"
RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"
#RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Scanian_War"
TEMP_IMAGES_FOLDER = "/tmp/images"
TEMP_SPEECH_FILE = "/tmp/speech.mp3"
HEADERS = {"Host": "upload.wikimedia.org", "Referer": "https://en.wikipedia.org/", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"}

def error(msg: str) -> None:
    print("ERROR: " + msg)
    sys.exit(1)

def get_text(content: BeautifulSoup) -> str:
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
        if "https:" + i["src"] in imgs:
            continue
        if not i["src"].startswith("//upload.wikimedia.org/wikipedia"):
            continue
        if i["src"].strip().endswith("-Red_pog.svg.png"):
            continue
        if i["src"].strip().endswith("-Yes_check.svg.png"):
            continue
        if i["src"].strip().endswith("UI_icon_edit-ltr-progressive.svg.png"):
            continue
        if i["src"].strip().endswith("-Wikispecies-logo.svg.png"):
            continue
        if i["src"].strip().endswith("Red_Pencil_Icon.png"):
            continue
        if i["src"].endswith(".svg.png"):
            parts = i["src"].split("/")
            parts[-1] = re.sub("([1-9][0-9]?)px", "100px", parts[-1])
            if "https:" + "/".join(parts) in imgs:
                continue
            imgs.append("https:" + "/".join(parts))
            score += 0.2
            continue
        h = f"{i['src'].split('/')[-4]}/{i['src'].split('/')[-3]}/"
        file = re.sub("^([0-9]*)px\\-", "", i["src"].split("/")[-1])
        imgs.append("https://upload.wikimedia.org/wikipedia/commons/" + h + file)
        score += 1
    print(f"{score}/{min_number}")
    if score < min_number:
        error("too few images")
    files = []
    for i in imgs:
        print(i)
        r = requests.get(i, stream=True, headers=HEADERS)
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
    text = get_text(soup)[:1000]
    min_imgs_number = len(text) / 300
    if min_imgs_number > 10: min_imgs_number = 10
    images = get_images(soup, min_imgs_number)

    print(url)
    print(title)
    print(text)

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(TEMP_SPEECH_FILE)

    image_args = ""
    random.shuffle(images)
    for i in images:
        pass

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    #[h, m, s] = [int(i) for i in subprocess.check_output(["sh", "-c", f"ffprobe -hide_banner {TEMP_SPEECH_FILE} 2>&1 | awk '/Duration/{{print $2}}' | cut -d. -f1"]).decode("utf-8").split(":")]
    #dur = s + (60*m) + (60*60*h)
    #max_per_image = int(dur / len(images))

    #img_args = ""
    #pos = 0
    #i = 0
    #clip = 1
    #while pos < dur:
    #    if i >= len(images):
    #        i = 0
    #    [w, h] = [int(j) for j in subprocess.check_output(["identify", "-format", "%w:%h", images[i]]).decode("utf-8").split(":")]
    #    aspect = w / h
    #    (width, height) = (int(aspect * 900), 900)
    #    if max_per_image < 1:
    #        see = 1
    #    else:
    #        see = max_per_image
    #    img_args += f" -i '{images[i]}' -filter_complex \"[{clip}:v] scale={width}x{height} [ovrl{clip}]; [0:v][ovrl{clip}] overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='between(t,{pos},{pos+see})'\""
    #    pos += see
    #    i += 1
    #    clip += 1

    command = f"/bin/ls /tmp/images/*.png | xargs -I§ sh -c 'convert § §.jpg && rm -v §'; ffmpeg -hide_banner -y -pattern_type glob -loop 1 -i '{TEMP_IMAGES_FOLDER}/*.jpg' -i \"{TEMP_SPEECH_FILE}\" -shortest {OUTPUT_FILE}"
    #command = f"ffmpeg -hide_banner" + \
    #        f" -loop 1 -i {BACKGROUND_IMAGE}" + \
    #        img_args + \
    #        f" -i {TEMP_SPEECH_FILE} -filter:a atempo=1.3" + \
    #        f" -t {dur} -vcodec mpeg4 {OUTPUT_FILE}"
    print(command)
    os.system(command)
    os.system(f"mpv {OUTPUT_FILE}")

