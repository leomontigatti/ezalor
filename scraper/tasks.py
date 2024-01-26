import json

import requests
from celery import Task, shared_task, states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from django.utils import timezone

from scraper.custom_pickle import fetch_new_articles
from scraper.models import (
    Article,
    FacebookPage,
    FacebookPost,
    InstagramPost,
    InstagramProfile,
)

logger = get_task_logger(__name__)


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = 10


def get_post_caption(article) -> str:
    """
    Return a string containing the caption text for the post body depending
    on the :model:`scraper.FacebookPage`
    """

    return (
        f"{article.title}\n\n{article.body}\n\nCONTINUAR LEYENDO LA NOTA: {article.url}\n\nFUENTE: {article.news_page.url}\n\n👉 En twitter @CNNRadioVCP\n\n👉 Escuchanos en FM 106.9, en www.cnnradio.com.ar o descargá la App en app.cnnradio.com.ar\n\n#CNNRadioVCP #CNNRadioVillaCarlosPaz #CNNRadioCarlosPaz",
    )


@shared_task(bind=True)
def fetch_new_articles_task(self) -> None:
    """
    Search all :model:`scraper.NewsPage` instances for new articles.
    """

    total_created: int = fetch_new_articles()
    self.update_state(
        state=states.SUCCESS, meta=f"Successfully created {total_created} articles."
    )
    logger.info(f"Successfully created {total_created} articles.")


@shared_task(bind=True, base=BaseTaskWithRetry)
def create_facebook_post_task(self, article_id: int, facebook_page_id: int) -> None:
    """
    Create a Facebook post for selected :model:`scraper.Article` instance.
    """

    facebook_page = FacebookPage.objects.get(pk=facebook_page_id)
    article = Article.objects.get(pk=article_id)

    if article.is_facebook:
        self.update_state(
            state=states.FAILURE,
            meta="Selected article already has a related Facebook post.",
        )
        logger.error("Selected article already has a related Facebook post.")
        raise Ignore()
    else:
        request = requests.post(
            url=f"https://graph.facebook.com/{facebook_page.page_id}/photos",
            params={
                "caption": get_post_caption(article),
                "access_token": facebook_page.page_token,
                "url": article.image,
            },
        )
        response_dict: dict = json.loads(request.text)

        if "error" in response_dict.keys():
            raise Exception(response_dict.get("error").get("message"))
        else:
            FacebookPost.objects.create(
                article=article,
                page=facebook_page,
                post_date=timezone.now(),
                post_id=response_dict.get("post_id"),
            )
            article.is_facebook = True
            article.save()
            logger.info("Facebook post successfully created.")


@shared_task(base=BaseTaskWithRetry)
def delete_facebook_post_task(facebook_post_id: str, facebook_page_id) -> None:
    """
    Delete a Facebook post given the :model:`scraper.FacebookPost` instance.
    Facebook does not yet support delete via their API. Please see the content publishing API.
    """

    facebook_page = FacebookPage.objects.get(pk=facebook_page_id)

    request = requests.delete(
        url=f"https://graph.facebook.com/{facebook_post_id}",
        params={"access_token": facebook_page.page_token},
    )
    response_dict: dict = json.loads(request.text)
    if "error" in response_dict.keys():
        raise Exception(response_dict.get("error").get("message"))
    else:
        logger.info("Facebook post successfully deleted.")


@shared_task(bind=True, base=BaseTaskWithRetry)
def create_instagram_post_task(
    self, article_id: int, instagram_profile_id: int
) -> None:
    """
    Create an Instagram post for selected :model:`scraper.Article` instance.
    """

    instagram_profile = InstagramProfile.objects.get(pk=instagram_profile_id)
    article = Article.objects.get(pk=article_id)

    if article.is_instagram:
        self.update_state(
            state=states.FAILURE,
            meta="Selected article already has a related Instagram post.",
        )
        logger.error("Selected article already has a related Instagram post.")
        raise Ignore()
    else:
        container_request = requests.post(
            url=f"https://graph.facebook.com/{instagram_profile.user_id}/media",
            params={
                "image_url": article.image,
                "caption": f"{article.title}\n\n{article.body}\n\nCONTINUAR LEYENDO LA NOTA: {article.url}\n\nFUENTE: {article.news_page.url}\n\n👉 En twitter @CNNRadioVCP\n\n👉 Escuchanos en FM 106.9, en www.cnnradio.com.ar o descargá la App en app.cnnradio.com.ar\n\n#CNNRadioVCP #CNNRadioVillaCarlosPaz #CNNRadioCarlosPaz",
                "access_token": instagram_profile.user_token,
            },
        )
        container_response_dict: dict = json.loads(container_request.text)

        if "error" in container_response_dict.keys():
            raise Exception(container_response_dict.get("error").get("message"))
        else:
            media_request = requests.post(
                url=f"https://graph.facebook.com/{instagram_profile.user_id}/media_publish",
                params={
                    "creation_id": container_response_dict.get("id"),
                    "access_token": instagram_profile.user_token,
                },
            )
            media_response_dict: dict = json.loads(media_request.text)

            if "error" in media_response_dict.keys():
                raise Exception(container_response_dict.get("error").get("message"))
            else:
                InstagramPost.objects.create(
                    article=article,
                    profile=instagram_profile,
                    post_date=timezone.now(),
                    post_id=media_response_dict.get("id"),
                )
                article.is_instagram = True
                article.save()
                logger.info("Instagram post successfully created.")


@shared_task
def auto_create_posts_task() -> None:
    facebook_pages_list: list[FacebookPage] = FacebookPage.objects.all()
    instagram_profiles_list: list[InstagramProfile] = InstagramProfile.objects.all()
    not_posted_articles_list: list[Article] = Article.objects.filter(
        post_date=timezone.now().date()
    ).filter(is_facebook=False, is_instagram=False)
    if not_posted_articles_list.exists():
        for facebook_page in facebook_pages_list:
            for article in not_posted_articles_list:
                create_facebook_post_task.delay(article.id, facebook_page.id)
        for instagram_profile in instagram_profiles_list:
            for article in not_posted_articles_list:
                create_instagram_post_task.delay(article.id, instagram_profile.id)
