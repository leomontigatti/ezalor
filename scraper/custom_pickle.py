import locale
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup, Tag

from scraper.models import Article, NewsPage

locale.setlocale(locale.LC_TIME, "es_AR.UTF-8")


def get_article_id(news_page: NewsPage, article: Tag) -> str:
    """
    Search and return the news page's article ID depending on the
    :model:`scraper.NewsPage`.
    """

    if news_page.id == 1:
        filtered = filter(lambda x: x.startswith("post-"), article["class"])
        for article_class in filtered:
            return article_class[5:]
    elif news_page.id == 2:
        filtered = filter(lambda x: x.startswith("postid-"), article.body["class"])
        for article_class in filtered:
            return article_class[7:]
    elif news_page.id == 3:
        a_tag = article.find(class_="linkpreviewnoticia").a.get("href")
        return a_tag.split("=")[-1]


def get_article_post_date(news_page: NewsPage, article: Tag) -> date:
    """
    Search and return the news page's article post date depending on the
    :model:`scraper.NewsPage`.
    """

    if news_page.id == 1:
        post_date_tag: Tag = article.find(class_="elementor-post-date")
        post_date_str: str = post_date_tag.get_text().strip()
        return datetime.strptime(post_date_str, "%d/%m/%Y").date()
    elif news_page.id == 2:
        post_date_tag: Tag = article.find("span", class_="fecha")
        post_date_str: str = post_date_tag.text
        return datetime.strptime(post_date_str, "%d de %B, %Y").date()
    elif news_page.id == 3:
        post_date_str: str = article.text[:10]
        return datetime.strptime(post_date_str, "%d/%m/%Y").date()


def fetch_new_articles() -> int:
    """
    Search all :model:`scraper.NewsPage` and create a new :model:`scraper.Article`
    instance if new depending on the news page.
    Return the number of created articles.
    """

    total_created: int = 0

    for page in NewsPage.objects.all():
        get_request = requests.get(url=page.url)
        soup = BeautifulSoup(get_request.text, "lxml")
        articles_list: list[Tag] = soup.find_all("article")
        if page.id == 1:
            for article in articles_list:
                if get_article_post_date(page, article) == date.today():
                    a, created = Article.objects.get_or_create(
                        id_number=get_article_id(page, article),
                        news_page=page,
                        defaults={
                            "url": article.find(
                                class_="elementor-post__thumbnail__link"
                            ).get("href"),
                            "title": article.h3.get_text().strip(),
                            "post_date": date.today(),
                            "image": article.img.get("src"),
                            "body": article.p.get_text().strip(),
                        },
                    )
                    if created:
                        total_created += 1

        elif page.id == 2:
            for article in articles_list:
                article_url: str = article.a.get("href")
                article_request = requests.get(url=article_url)
                article_ = BeautifulSoup(article_request.text, "lxml")
                if get_article_post_date(page, article_) == date.today():
                    a, created = Article.objects.get_or_create(
                        id_number=get_article_id(page, article_),
                        news_page=page,
                        defaults={
                            "url": article_url,
                            "title": article_.h1.text,
                            "post_date": date.today(),
                            "image": article_.find(
                                "img", class_="attachment-post-thumbnail"
                            ).get("data-src"),
                            "body": article_.find(id="dslc-theme-content-inner").p.text,
                        },
                    )
                    if created:
                        total_created += 1

        elif page.id == 3:
            articles_list: list[Tag] = soup.find_all(class_="titulopreviewnoticia")
            for article in articles_list:
                body_tag: Tag = article.next_sibling.next_sibling
                if get_article_post_date(page, article) == date.today():
                    a, created = Article.objects.get_or_create(
                        id_number=get_article_id(page, body_tag),
                        news_page=page,
                        defaults={
                            "url": page.url[:34]
                            + body_tag.find(class_="linkpreviewnoticia").a.get("href"),
                            "title": article.text[13:],
                            "post_date": date.today(),
                            "image": "https://i.postimg.cc/vB77SY4G/RECUADRO-NOTICIA-CNN.png",
                            "body": body_tag.find(
                                class_="descripcionpreviewnoticia"
                            ).p.text,
                        },
                    )
                    if created:
                        total_created += 1

    return total_created
