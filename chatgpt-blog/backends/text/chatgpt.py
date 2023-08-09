
from revChatGPT.V1 import Chatbot
import json
import os

from .text import ArticleText

class TextBackendChatGPT:
    def __init__(self) -> None:
        self.CACHE_DIR = os.path.expanduser("~/.cache/chatgpt-blog")
        self.TOPICS_CACHE_FILE = os.path.join(self.CACHE_DIR, "topics.json")
        self.bot = Chatbot(self.read_json_file(os.path.expanduser("~/.config/revChatGPT/config.json")))
        self.CONVERSATION_ID = self.read_json_file(os.path.expanduser("~/.config/revChatGPT/config.json"))["conversation_id"]
        self.PROMPT_TEMPLATES = {
            "ideas": "What are five unique article ideas for a tech blog? Only give the titles.",
            "image_idea": "What could an image lokk like that visualizes an article with title '{title}'? Give a short, one-paragraph description, which is still very detailed.",
            "image_caption": "Condense the following text down to five words: '{desc}'",
            "article": "Write an article for a tech blog with following title: '{title}'; continuous, but structured text; introduction and conclusion; avoid listings and headings"
        }

    def ask(self, prompt) -> str:
        try:
            for data in self.bot.ask(prompt, conversation_id=self.CONVERSATION_ID):
                resp = data["message"]
        except Exception:
            print("failed to ask ChatGPT. Do you have a valid session (press enter to proceed)?")
            input()
            return self.ask(prompt)
        return resp

    def read_json_file(self, path: str) -> any:
        with open(path) as f:
            return json.load(f)

    def read_json_list_file(self, path: str) -> any:
        return [i.strip() for i in self.read_json_file(path) if i.strip() != ""]

    def write_json_list_file(self, path: str, data: list) -> any:
        json.dump(data, open(path, "w"))

    def get_topic(self) -> str:
        if not os.path.isfile(self.TOPICS_CACHE_FILE) or len(self.read_json_list_file(self.TOPICS_CACHE_FILE)) < 1:
            resp = self.ask(self.PROMPT_TEMPLATES["ideas"].format())
            topics = [i[2:] for i in resp.split("\n") if not i.startswith("Sure, ")]
            self.write_json_list_file(self.TOPICS_CACHE_FILE, topics)
        topics = self.read_json_list_file(self.TOPICS_CACHE_FILE)
        self.write_json_list_file(self.TOPICS_CACHE_FILE, topics[1:])
        return topics[0].strip("\"").strip("'")

    def get_body(self, title: str) -> str:
        text = self.ask(self.PROMPT_TEMPLATES["article"].format(title=title))
        text = "\n".join([l for l in text.split("\n") if l.strip() not in ("Conclusion:", "Introduction:", "Body:")])
        return ArticleText(self.ask(self.PROMPT_TEMPLATES["article"].format(title=title)), title, "ChatGPT")

    def get_image_idea(self, title: str) -> str:
        resp = self.ask(self.PROMPT_TEMPLATES["image_idea"].format(title=title))
        joined = ""
        for line in resp.split("\n"):
            if line.startswith("As an AI language model"):
                continue
            joined += line
        return joined.strip()

    def get_caption(self, desc: str) -> str:
        return self.ask(self.PROMPT_TEMPLATES["image_caption"].format(desc=desc))
