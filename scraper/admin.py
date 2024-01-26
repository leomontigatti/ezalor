from django.contrib import admin, messages

from scraper.models import (
    Article,
    FacebookPage,
    FacebookPost,
    InstagramPost,
    InstagramProfile,
    NewsPage,
)
from scraper.tasks import create_facebook_post_task, create_instagram_post_task


def create_facebook_posts(facebook_page: FacebookPage) -> tuple:
    """
    Admin action related to :model:`scraper.Article` to post selected
    articles in a specific :model:`scraper.FacebookPage`.
    """

    name: str = f"facebook_post_{facebook_page}"

    def create_facebook_posts_action(modeladmin, request, queryset):
        articles_id_list: list[int] = [article.id for article in queryset]
        modeladmin.message_user(
            request,
            "Se están creando las publicaciones en Facebook de todos los artículos seleccionados.",
            messages.SUCCESS,
        )
        for article_id in articles_id_list:
            create_facebook_post_task.delay(article_id, facebook_page.id)

    return (
        name,
        (
            create_facebook_posts_action,
            name,
            f"Publicar en Facebook: {facebook_page.name}",
        ),
    )


def create_instagram_posts(instagram_profile: InstagramProfile) -> tuple:
    """
    Admin action related to :model:`scraper.Article` to post selected
    articles in a specific :model:`scraper.InstagramProfile`.
    """

    name: str = f"instagram_post_{instagram_profile}"

    def create_instagram_posts_action(modeladmin, request, queryset):
        articles_id_list: list[int] = [article.id for article in queryset]
        modeladmin.message_user(
            request,
            "Se están creando las publicaciones en Instagram de todos los artículos seleccionados.",
            messages.SUCCESS,
        )
        for article_id in articles_id_list:
            create_instagram_post_task.delay(article_id, instagram_profile.id)

    return (
        name,
        (
            create_instagram_posts_action,
            name,
            f"Publicar en Instagram: {instagram_profile.name}",
        ),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.Article`.
    """

    # List view.
    list_display: tuple = (
        "post_date",
        "id_number",
        "news_page",
        "title",
        "is_facebook",
        "is_instagram",
    )
    list_filter: tuple = (
        "post_date",
        "news_page",
        "is_facebook",
        "is_instagram",
    )
    list_display_links: tuple = ("id_number", "title")
    search_fields: tuple = ("post_date", "title")
    search_help_text: str = "Buscar por fecha de publicación o título."

    def get_actions(self, request) -> dict:
        actions = super(ArticleAdmin, self).get_actions(request)  # If any
        facebook_profile_list = FacebookPage.objects.all()
        instagram_profile_list = InstagramProfile.objects.all()
        return {
            **actions,
            **dict(
                create_facebook_posts(facebook_profile)
                for facebook_profile in facebook_profile_list
            ),
            **dict(
                create_instagram_posts(instagram_profile)
                for instagram_profile in instagram_profile_list
            ),
        }

    # Add/change view.
    fieldsets: tuple = (
        (
            "General",
            {
                "fields": (
                    ("news_page", "id_number"),
                    ("title", "post_date"),
                    "url",
                    "body",
                    "image",
                    ("is_facebook", "is_instagram"),
                )
            },
        ),
    )

    class FacebookPostInline(admin.TabularInline):
        model: FacebookPost = FacebookPost
        fk_name: str = "article"
        extra: int = 0

    class InstagramPostInline(admin.TabularInline):
        model: InstagramPost = InstagramPost
        fk_name: str = "article"
        extra: int = 0

    inlines: tuple = (FacebookPostInline, InstagramPostInline)


@admin.register(NewsPage)
class NewsPageAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.NewsPage`.
    """

    # List view.
    list_display: tuple = (
        "id",
        "name",
        "url",
    )
    list_display_links: tuple = ("name",)


@admin.register(FacebookPage)
class FacebookPageAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.FacebookPage`.
    """

    pass


@admin.register(InstagramProfile)
class InstagramProfileAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.InstagramProfile`.
    """

    pass


@admin.register(FacebookPost)
class FacebookPostAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.FacebookPost`.
    """

    # List view.
    list_display: tuple = (
        "article",
        "page",
        "post_date",
    )
    list_filter: tuple = (
        "page",
        "post_date",
    )
    list_display_links: tuple = ("article",)
    search_fields: tuple = ("post_date", "post_id")
    search_help_text: str = "Buscar por fecha o ID de publicación."


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    """
    Admin model related to :model:`scraper.InstagramPost`.
    """

    # List view.
    list_display: tuple = (
        "article",
        "profile",
        "post_date",
    )
    list_filter: tuple = (
        "profile",
        "post_date",
    )
    list_display_links: tuple = ("article",)
    search_fields: tuple = ("post_date", "post_id")
    search_help_text: str = "Buscar por fecha o ID de publicación."
