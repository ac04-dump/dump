
from datetime import datetime
import os

from backends.text import TextBackendChatGPT
from backends.image import ImageBackendStableDiffusionWebui


class BlogGenerator:
    def __init__(self) -> None:
        print("Initializing...")
        self.OUTPUT_DIR = os.getenv("BLOG_OUTPUT_DIR")
        if self.OUTPUT_DIR is None or self.OUTPUT_DIR.strip() == "":
            self.OUTPUT_DIR = "./out"
        self.TEMPDIR = "/media/temp"
        self.blog_name = "Techtopia Today"
        self.url_prefix = "techtopia-today"
        self.text_backend = TextBackendChatGPT()
        self.image_backend = ImageBackendStableDiffusionWebui()
    
    def article_title(self, name: str) -> dict:
        with open(os.path.join(self.OUTPUT_DIR, "articles", name), "r") as f:
            while True:
                line = f.readline().strip()
                if not line.startswith("<title>"):
                    continue
                return line.replace("<title>", "").replace("</title>", "")

    def get_articles_list(self) -> list:
        files = os.listdir(os.path.join(self.OUTPUT_DIR, "articles"))
        files.sort()
        res = []
        for f in files:
            res.append(f"<li><a href=\"/{self.url_prefix}/articles/{f}\">{self.article_title(f)}</a></li>")
        return res

    def write_article(self) -> None:
        print("Finding a topic...")
        id_ = datetime.now().strftime("%Y-%m-%d-%H-%M")
        title = self.text_backend.get_topic()

        print(f"Writing article with title: '{title}'...")
        article = self.text_backend.get_body(title)
        with open(os.path.join(self.TEMPDIR, "article.txt"), "w") as f:
            f.write(article.body_raw())

        print("Finding idea for image...")
        img_description = self.text_backend.get_image_idea(title)

        img_html = ""
        if img_description != "":
            img_caption = self.text_backend.get_caption(img_description)
            print("Generating image...")
            img = self.image_backend.get_image(img_description, img_caption, id_, self.OUTPUT_DIR)
            if img is not None:
                img_data = img.to_html(self.url_prefix)
        else:
            print("No usable image description provided, skipping image generation")

        print("Assembling article...")
        with open(f"{self.OUTPUT_DIR}/articles/{id_}.html", "w") as of:
            of.write(article.to_html(img_data, self.blog_name, self.url_prefix, template="templates/article.html"))

        print("Updating index page...")
        with open("templates/index.html", "r") as t:
            with open(os.path.join(self.OUTPUT_DIR, "index.html"), "w") as f:
                f.write(t.read().format(blog_name=self.blog_name, articles="\n".join(self.get_articles_list()), url_prefix=self.url_prefix))

        print("Updating stylesheets...")
        for f in os.listdir("templates/css"):
            os.system(f"cp './templates/css/{f}' '{self.OUTPUT_DIR}/static/css/{f}'")
        
