import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "id_number",
                    models.CharField(max_length=20, verbose_name="Número de ID"),
                ),
                ("url", models.URLField(verbose_name="URL")),
                ("title", models.CharField(max_length=200, verbose_name="Título")),
                ("post_date", models.DateField(verbose_name="Fecha de publicación")),
                ("image", models.URLField(verbose_name="Imágen")),
                ("body", models.TextField(verbose_name="Cuerpo")),
                (
                    "is_facebook",
                    models.BooleanField(default=False, verbose_name="Facebook"),
                ),
                (
                    "is_instagram",
                    models.BooleanField(default=False, verbose_name="Instagram"),
                ),
            ],
            options={
                "verbose_name": "Artículo",
                "verbose_name_plural": "Artículos",
                "ordering": ("-post_date", "-id"),
            },
        ),
        migrations.CreateModel(
            name="FacebookPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Nombre")),
                (
                    "page_id",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="ID de página"
                    ),
                ),
                (
                    "page_token",
                    models.CharField(
                        help_text='<a href="https://developers.facebook.com/tools/debug/accesstoken/" target="_blank">Revisar validez</a>',
                        max_length=300,
                        verbose_name="Token de página",
                    ),
                ),
            ],
            options={
                "verbose_name": "Página de Facebook",
                "verbose_name_plural": "Páginas de Facebook",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="InstagramProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Nombre")),
                (
                    "user_id",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="ID de usuario"
                    ),
                ),
                (
                    "user_token",
                    models.CharField(
                        help_text='<a href="https://developers.facebook.com/tools/debug/accesstoken/" target="_blank">Revisar validez</a>',
                        max_length=300,
                        verbose_name="Token de usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de Instagram",
                "verbose_name_plural": "Perfiles de Instagram",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="NewsPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Nombre")),
                ("url", models.URLField(verbose_name="URL")),
            ],
            options={
                "verbose_name": "Página de noticias",
                "verbose_name_plural": "Páginas de noticias",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="FacebookPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "post_date",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Fecha y hora de publicación",
                    ),
                ),
                (
                    "post_id",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="ID de publicación",
                    ),
                ),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="facebook_posts",
                        to="scraper.article",
                        verbose_name="Artículo",
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="facebook_posts",
                        to="scraper.facebookpage",
                        verbose_name="Página de Facebook",
                    ),
                ),
            ],
            options={
                "verbose_name": "Publicación en Facebook",
                "verbose_name_plural": "Publicaciones en Facebook",
                "ordering": ("post_id", "article"),
            },
        ),
        migrations.CreateModel(
            name="InstagramPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "post_date",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Fecha y hora de publicación",
                    ),
                ),
                (
                    "post_id",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="ID de publicación",
                    ),
                ),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="instagram_posts",
                        to="scraper.article",
                        verbose_name="Artículo",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="instagram_posts",
                        to="scraper.instagramprofile",
                        verbose_name="Perfil de Instagram",
                    ),
                ),
            ],
            options={
                "verbose_name": "Publicación en Instagram",
                "verbose_name_plural": "Publicaciones en Instagram",
                "ordering": ("post_id", "article"),
            },
        ),
        migrations.AddField(
            model_name="article",
            name="news_page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="articles",
                to="scraper.newspage",
                verbose_name="Página de noticias",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="article",
            unique_together={("id_number", "news_page")},
        ),
    ]
