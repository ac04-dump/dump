#!/usr/bin/env python3

from bs4 import BeautifulSoup
from gtts import gTTS
import os
import re
import requests
import sys

RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"
TEMP_SPEECH_FILE = "/tmp/speech.mp3"

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
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(TEMP_SPEECH_FILE)
    return text

def get_images(content: BeautifulSoup, min_number: int) -> list:
    imgs = content.find_all("img")
    for i in imgs:
        if not i["src"].startswith("//upload.wikimedia.org/wikipedia"):
            continue
        print("https:" + i["src"])

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
    #text = generate_speech(soup)
    images = get_images(soup, 3)

    print(url)
    print(title)
    #print(text)

    #os.system(f"mpv --speed=1.3 {TEMP_SPEECH_FILE}")

