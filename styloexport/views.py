from pathlib import Path
from typing import Any, Tuple, Type, TypeVar, Union

import httpx
from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from slugify import slugify
from werkzeug.wrappers.response import Response
from wtforms import validators

from .article import Article
from .forms import (
    ArticleForm,
    EditionForm,
    ExportForm,
    ExportGeneriqueForm,
    ExportRevueForm,
)
from .pandocapi import PandocAPI
from .utils import get_bibliographic_styles_choices, get_domain_from_url, get_env_var

blueprint = Blueprint("views", __name__)
E = TypeVar("E", bound=ExportForm)

fake_path = Path()
pandocapi = PandocAPI(fake_path, fake_path, fake_path)


@blueprint.route("/", methods=("GET", "POST"))
def index() -> Union[str, Response]:
    editions = current_app.config.get("SE_EDITIONS", [])
    form = EditionForm()
    editions_choices = [(slug, metadata["name"]) for slug, metadata in editions.items()]
    form.edition.choices = editions_choices

    if form.validate_on_submit():
        edition = form.edition.data

        return redirect(url_for("views.edition", edition=edition))

    return render_template("index.html", **{"form": form, "editions": editions_choices})


@blueprint.route("/<edition>/", methods=("GET", "POST"))
def edition(edition: str) -> Union[str, Response]:
    SE_ALLOWED_INSTANCE_BASE_URLS_STR = get_env_var("SE_ALLOWED_INSTANCE_BASE_URLS")
    SE_ALLOWED_INSTANCE_BASE_URLS = SE_ALLOWED_INSTANCE_BASE_URLS_STR.split(" ")

    form = ArticleForm()
    form.domain.choices = [
        (get_domain_from_url(url), get_domain_from_url(url))
        for url in SE_ALLOWED_INSTANCE_BASE_URLS
    ]

    if form.validate_on_submit():
        slug = slugify(form.name.data, lowercase=False)
        kind = form.kind.data
        domain = form.domain.data
        article_id = form.article_id.data
        with_toc = form.with_toc.data
        with_ascii = form.with_ascii.data

        return redirect(
            url_for(
                f"views.{kind}",
                edition=edition,
                domain=domain,
                article_id=article_id,
                article_slug=slug,
                with_toc=1 if with_toc else 0,
                with_ascii=1 if with_ascii else 0,
            )
        )

    return render_template(
        "edition.html",
        **{
            "edition": edition,
            "form": form,
        },
    )


def get_article(
    edition: str,
    domain: str,
    article_id: str,
    article_slug: str,
    editions: dict,
    edition_configuration: dict,
    force_download: bool,
) -> Article:
    SE_ALLOWED_INSTANCE_BASE_URLS_STR = get_env_var("SE_ALLOWED_INSTANCE_BASE_URLS")
    SE_ALLOWED_INSTANCE_BASE_URLS = SE_ALLOWED_INSTANCE_BASE_URLS_STR.split(" ")
    SE_DOWNLOAD_DIR = current_app.config["SE_DOWNLOAD_DIR"]
    SE_SUPPORTED_IMAGES_EXTENSIONS = current_app.config.get(
        "SE_SUPPORTED_IMAGES_EXTENSIONS", []
    )
    templates_folder = (Path() / "templates" / edition).resolve()
    article_title = ""
    article = Article(
        edition,
        edition_configuration,
        domain,
        article_id,
        article_slug,
        article_title,
        SE_DOWNLOAD_DIR,
        list(editions.keys()),
        SE_ALLOWED_INSTANCE_BASE_URLS,
        SE_SUPPORTED_IMAGES_EXTENSIONS,
    )
    article.fetch_all(templates_folder, force=force_download)
    return article


def get_form(
    edition: str, article: Article, edition_configuration: dict
) -> Union[ExportGeneriqueForm, ExportRevueForm]:
    is_generic = edition == "generique"
    form_class: Type[Union[ExportGeneriqueForm, ExportRevueForm]] = (
        ExportGeneriqueForm if is_generic else ExportRevueForm
    )
    form = form_class(formdata=request.args)

    if is_generic:
        formats_choices = edition_configuration["exports"]
    else:
        formats_choices = [
            (slug, metadata["name"])
            for slug, metadata in edition_configuration["exports"].items()
        ]
    form.formats.choices = formats_choices

    if "bibliography_style" in form:
        form.bibliography_style.choices = get_bibliographic_styles_choices()

    version_choices = [("", "Version la plus récente")]
    for version in article.versions:
        version_label = (
            f"{version['message'] or 'Version sans nom'} "
            f"- {version['version']}.{version['revision']}"
        )
        version_choices.append((version["_id"], version_label))

    form.version.choices = version_choices
    # Dynamic validator because allowed version values are dynamic.
    form.version.validators = [
        validators.AnyOf(
            values=list(dict(version_choices).keys()),
            message="Version incorrecte, choix possibles : %(values)s.",
        )
    ]

    return form


def generate_bibliography(
    article: Article, form: Union[ExportGeneriqueForm, ExportRevueForm]
) -> Tuple[str, str]:
    bibliography_excerpt = ""
    bibliography_preview = ""

    if "bibliography_style" in form and not article.errors:

        def get_only_first_entries(
            content: str, separator: str = "\n\n", number: int = 3
        ) -> str:
            splited = content.split(separator, number)
            return separator.join(splited[:number])

        bibliography_excerpt = get_only_first_entries(
            article.bib_original_filepath.read_text()
        )

        if bibliography_excerpt.strip():
            try:
                bibliography_style = "chicagomodified"
                response = pandocapi.bibliography(
                    bibliography_excerpt,
                    bibliography_style,
                    current_app.config["SE_STYLES_DIR"] / f"{bibliography_style}.csl",
                )
                bibliography_preview = response.content.decode()
            except httpx.HTTPError:
                bibliography_preview = "La génération de la prévisualisation a échoué."

    return bibliography_excerpt, bibliography_preview


@blueprint.route(
    "/<edition>/article/<domain>/<article_id>/<article_slug>/", methods=("GET",)
)
def article(edition: str, domain: str, article_id: str, article_slug: str) -> str:
    force_download = bool(request.args.get("force_download", False))
    editions = current_app.config["SE_EDITIONS"]
    edition_configuration = editions[edition]
    article = get_article(
        edition,
        domain,
        article_id,
        article_slug,
        editions,
        edition_configuration,
        force_download,
    )
    form = get_form(edition, article, edition_configuration)
    bibliography_excerpt, bibliography_preview = generate_bibliography(article, form)

    return render_template(
        "article.html",
        **{
            "article": article,
            "bibliography_excerpt": bibliography_excerpt,
            "bibliography_preview": bibliography_preview,
            "form": form,
        },
    )


@blueprint.route(
    "/<edition>/export/<domain>/<article_id>/<article_slug>/", methods=("GET",)
)
def export(edition: str, domain: str, article_id: str, article_slug: str) -> Any:
    print("exporting: " + edition + " " + domain + " " + article_id + " " + article_slug)
    force_download = bool(request.args.get("force_download", False))
    editions = current_app.config["SE_EDITIONS"]
    edition_configuration = editions[edition]
    article = get_article(
        edition,
        domain,
        article_id,
        article_slug,
        editions,
        edition_configuration,
        force_download,
    )
    form = get_form(edition, article, edition_configuration)
    if form.validate():
        version = form.version.data
        with_toc = form.with_toc.data
        with_ascii = form.with_ascii.data
        format_kind = form.formats.data
        templates_folder = (Path() / "templates" / edition).resolve()
        if edition == "generique":
            formats = format_kind
            style_name = form.bibliography_style.data
        else:
            formats = edition_configuration["exports"][format_kind]["formats"]
            csl_file_path = next(templates_folder.glob("*.csl"))
            style_name = csl_file_path.stem
        export_file_path = article.export(
            version,
            formats,
            style_name,
            templates_folder,
            with_toc=with_toc,
            with_ascii=with_ascii,
        )
        if article.errors:
            return render_template("article.html", **{"article": article, "form": form})
    else:
        return render_template("article.html", **{"article": article, "form": form})

    return send_file(export_file_path, as_attachment=True)


@blueprint.route(
    "/<edition>/downloads/<domain>/<article_id>/<article_slug>/<path:filename>",
    methods=("GET",),
)
def downloads(
    edition: str, domain: str, article_id: str, article_slug: str, filename: str
) -> Any:
    download_dir = (Path("..") / current_app.config["SE_DOWNLOAD_DIR"]).resolve()
    download_file_path = (
        download_dir / edition / domain / f"{article_slug}-{article_id}" / filename
    )
    # print(download_file_path)
    if not download_file_path.exists():
        return abort(404)

    return send_file(download_file_path, as_attachment=True)
