from django.db.models.signals import post_delete
from django.dispatch import receiver

from scraper.models import Article, FacebookPost, InstagramPost


@receiver(post_delete, sender=FacebookPost, weak=False)
def delete_facebook_post_signal(sender, instance, **kwargs):
    """
    Delete a Facebook post after :model:`scraper.FacebookPost` instance
    is deleted.
    Update is_facebook if there are no Facebook posts related to
    :model:`scraper.Article`.
    """

    # Facebook does not yet support delete via their API. Please see the content publishing API.

    article: Article = instance.article
    if not article.facebook_posts.exists():
        article.is_facebook = False
        article.save()


@receiver(post_delete, sender=InstagramPost, weak=False)
def delete_instagram_post_signal(sender, instance, **kwargs):
    """
    Update is_instagram if there are no Instagram posts related to
    :model:`scraper.Article`.
    """

    # Instagram does not yet support delete via their API. Please see the content publishing API.

    article: Article = instance.article
    if not article.instagram_posts.exists():
        article.is_instagram = False
        article.save()
