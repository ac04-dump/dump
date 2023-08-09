
class ArticleText:
    def __init__(self, body: str, title: str, author: str) -> None:
        self.body = body
        self.title = title
        self.author = author

    def _body_to_html(self) -> str:
        return "\n".join([f"<p>{p}</p>" for p in self.body.split("\n") if p.strip() != ""])

    def body_raw(self) -> str:
        return self.body

    def to_html(self, image_html: str, blog_name: str, url_prefix: str, template: str = "templates/article.html") -> str:
        with open(template, "r") as t:
            return t.read().format(title=self.title, body=self._body_to_html(), image=image_html, author=self.author, blog_name=blog_name, url_prefix=url_prefix)
