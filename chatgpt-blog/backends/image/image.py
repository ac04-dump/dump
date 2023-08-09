
class ArticleImage:
    def __init__(self, id_: str, caption: str, author: str, prompt: str) -> None:
        self.id_ = id_
        self.caption = caption
        self.author = author
        self.prompt = prompt

    def to_html(self, url_prefix: str) -> str:
        return f"""
<figure>
  <img src="/{url_prefix}/static/images/{self.id_}.png" alt="{self.caption}" style="width=100%;">
  <span hidden class="image-generation-prompt">{self.prompt}</span>
  <figcaption>"{self.caption}" by {self.author}</figcaption>
</figure> 
"""

