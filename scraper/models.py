from datetime import date, datetime

from django.db import models
from django.utils.safestring import mark_safe


class NewsPage(models.Model):
    """
    Store a single news page instance, related to :model:`scraper.Article`.
    """

    name: str = models.CharField(verbose_name="Nombre", max_length=200)
    url: str = models.URLField(verbose_name="URL")

    class Meta:
        verbose_name: str = "Página de noticias"
        verbose_name_plural: str = "Páginas de noticias"
        ordering: tuple = ("id",)

    def __str__(self) -> str:
        return self.name


class FacebookPage(models.Model):
    """
    Store a single Facebook page instance.
    """

    name: str = models.CharField(verbose_name="Nombre", max_length=100)
    page_id: str = models.CharField(
        verbose_name="ID de página", max_length=100, unique=True
    )
    page_token: str = models.CharField(
        verbose_name="Token de página",
        max_length=300,
        help_text=mark_safe(
            '<a href="https://developers.facebook.com/tools/debug/accesstoken/" target="_blank">Revisar validez</a>'
        ),
    )

    class Meta:
        verbose_name: str = "Página de Facebook"
        verbose_name_plural: str = "Páginas de Facebook"
        ordering: tuple = ("name",)

    def __str__(self) -> str:
        return self.name


class InstagramProfile(models.Model):
    """
    Store a single Instagram profile instance.
    """

    name: str = models.CharField(verbose_name="Nombre", max_length=100)
    user_id: str = models.CharField(
        verbose_name="ID de usuario", max_length=100, unique=True
    )
    user_token: str = models.CharField(
        verbose_name="Token de usuario",
        max_length=300,
        help_text=mark_safe(
            '<a href="https://developers.facebook.com/tools/debug/accesstoken/" target="_blank">Revisar validez</a>'
        ),
    )

    class Meta:
        verbose_name: str = "Perfil de Instagram"
        verbose_name_plural: str = "Perfiles de Instagram"
        ordering: tuple = ("name",)

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    """
    Store a single article instance, related to :model:`scraper.NewsPage`.
    """

    id_number: str = models.CharField(verbose_name="Número de ID", max_length=20)
    news_page: int = models.ForeignKey(
        NewsPage,
        verbose_name="Página de noticias",
        on_delete=models.RESTRICT,
        related_name="articles",
    )
    url: str = models.URLField(verbose_name="URL")
    title: str = models.CharField(verbose_name="Título", max_length=200)
    post_date: date = models.DateField(verbose_name="Fecha de publicación")
    image: str = models.URLField(verbose_name="Imágen")
    body: str = models.TextField(verbose_name="Cuerpo")
    is_facebook: bool = models.BooleanField(verbose_name="Facebook", default=False)
    is_instagram: bool = models.BooleanField(verbose_name="Instagram", default=False)

    class Meta:
        verbose_name: str = "Artículo"
        verbose_name_plural: str = "Artículos"
        unique_together: tuple = (
            "id_number",
            "news_page",
        )
        ordering: tuple = (
            "-post_date",
            "-id",
        )

    def __str__(self) -> str:
        return self.title


class FacebookPost(models.Model):
    """
    Store a single Facebook post instance, related to :model:`scraper.Article`
    and :model:`scraper.FacebookPage`.
    """

    article: Article = models.ForeignKey(
        Article,
        verbose_name="Artículo",
        on_delete=models.RESTRICT,
        related_name="facebook_posts",
    )
    page: FacebookPage = models.ForeignKey(
        FacebookPage,
        verbose_name="Página de Facebook",
        on_delete=models.RESTRICT,
        related_name="facebook_posts",
    )
    post_date: datetime = models.DateTimeField(
        verbose_name="Fecha y hora de publicación", blank=True, null=True
    )
    post_id: str = models.CharField(
        verbose_name="ID de publicación", max_length=200, blank=True, null=True
    )

    class Meta:
        verbose_name: str = "Publicación en Facebook"
        verbose_name_plural: str = "Publicaciones en Facebook"
        ordering: tuple = ("post_id", "article")

    def __str__(self) -> str:
        return self.article.title


class InstagramPost(models.Model):
    """
    Store a single Instagram post instance, related to :model:`scraper.Article`
    and :model:`scraper.InstagramProfile`.
    """

    article: Article = models.ForeignKey(
        Article,
        verbose_name="Artículo",
        on_delete=models.RESTRICT,
        related_name="instagram_posts",
    )
    profile: InstagramProfile = models.ForeignKey(
        InstagramProfile,
        verbose_name="Perfil de Instagram",
        on_delete=models.RESTRICT,
        related_name="instagram_posts",
    )
    post_date: datetime = models.DateTimeField(
        verbose_name="Fecha y hora de publicación", blank=True, null=True
    )
    post_id: str = models.CharField(
        verbose_name="ID de publicación", max_length=200, blank=True, null=True
    )

    class Meta:
        verbose_name: str = "Publicación en Instagram"
        verbose_name_plural: str = "Publicaciones en Instagram"
        ordering: tuple = ("post_id", "article")

    def __str__(self) -> str:
        return self.article.title
