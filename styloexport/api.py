import http
import json
from pathlib import Path
from typing import List, Tuple

import httpx
from flask import Blueprint, current_app, request
from flask_cors import CORS

from .pandocapi import PandocAPI
from .utils import get_env_var

blueprint = Blueprint("api", __name__)
CORS(blueprint)

fake_path = Path()
pandocapi = PandocAPI(fake_path, fake_path, fake_path)


@blueprint.route("/available_exports", methods=("GET",))
def available_exports() -> List[dict]:
    """Return a list of available exports (HTML, PDF, etc).

    This is a way to expose the `SE_EDITIONS["generic"]["exports"]` setting.

    * Route: `/api/available_exports`
    * Method: GET
    * Parameters: None
    * Example response:

    ```json
    [
      {
        "key": "originals",
        "name": "fichiers originaux (md, yaml et bib)"
      },
      {
        "key": "html",
        "name": "conversion HTML"
      },
      {
        "key": "pdf",
        "name": "conversion PDF"
      },
      […]
    ]
    ```
    """
    se_editions = get_env_var("SE_EDITIONS")
    exports = se_editions["generique"]["exports"]
    return [{"key": key, "name": name} for key, name in exports]


@blueprint.route("/allowed_instance_base_urls", methods=("GET",))
def allowed_instance_base_urls() -> List[str]:
    """Return a list of allowed instance base URLs.

    This is a way to expose the `SE_ALLOWED_INSTANCE_BASE_URLS` setting.

    * Route: `/api/allowed_instance_base_urls`
    * Method: GET
    * Parameters: None
    * Example response:

    ```json
    [
      "https://stylo.huma-num.fr",
      "https://stylo-dev.huma-num.fr"
    ]
    ```
    """
    allowed_instance_base_urls: str = get_env_var("SE_ALLOWED_INSTANCE_BASE_URLS")
    return allowed_instance_base_urls.split(" ")


@blueprint.route("/available_bibliographic_styles", methods=("GET",))
def available_bibliographic_styles() -> List[dict]:
    """Return a list of available bibliographic styles.

    This is a way to expose the `SE_STYLES_DIR` setting + Chicago modified.

    * Route: `/api/available_bibliographic_styles`
    * Method: GET
    * Parameters: None
    * Example response:

    ```json
    [
      {
        "categories": {
          "fields": [
            "humanities"
          ],
          "format": ""
        },
        "dependent": 1,
        "href": "https://www.zotero.org/styles/chicagomodified",
        "name": "chicagomodified",
        "title": "Chicago (modified)",
        "updated": "2022-12-20 00:00:00"
      },
      {
        "categories": {
          "fields": [
            "humanities"
          ],
          "format": "author-date"
        },
        "dependent": 0,
        "href": "https://www.zotero.org/styles/↩
                 acme-an-international-journal-for-critical-geographies",
        "name": "acme-an-international-journal-for-critical-geographies",
        "title": "ACME: An International Journal for Critical Geographies",
        "updated": "2018-06-17 04:54:57"
      },
      […]
    ]
    ```
    """
    styles_dir = current_app.config["SE_STYLES_DIR"]
    styles_text = (styles_dir / "styles-custom.json").read_text()
    styles_json: List[dict] = json.loads(styles_text)
    styles_json.insert(
        0,
        {
            "title": "Chicago (modified)",
            "name": "chicagomodified",
            "dependent": 1,
            "categories": {"format": "", "fields": ["humanities"]},
            "updated": "2022-12-20 00:00:00",
            "href": "https://www.zotero.org/styles/chicagomodified",
        },
    )
    return styles_json


@blueprint.route("/bibliography_preview", methods=("POST",))
def bibliography_preview() -> Tuple[str, http.HTTPStatus]:
    """Convert a bibliography excerpt to HTML with a given style.

    This is a way to render a bibliography for instant preview.

    * Route: `/api/bibliography_preview`
    * Method: POST
    * Parameters:
        - `bibliography_style` (default: `chicagomodified`): the name/slug
          of the bibliographic style as defined by Zotero.
        - `excerpt`: the string containing the excerpt of the `.bib` file,
          for instance:
    ```
    @article{reggiani_2015,
        title = {{Trous} du livre, plénitude du sens ?},
        volume = {Formes : Supports/Espaces},
        number = {19},
        journal = {Revue Formules, Presses Universitaires du Nouveau Monde},
        author = {Reggiani, Christelle and Reig, Christophe and Thomas,↩
                  Jean-Jacques and Salceda, Hermès},
        year = {2015}
    }
    ```
    * Example response:

    ```html
    <div id="refs" class="references csl-bib-body hanging-indent"
    role="doc-bibliography">
    <div id="ref-reggiani_2015" class="csl-entry" role="doc-biblioentry">
    Reggiani, Christelle, Christophe Reig, Jean-Jacques Thomas, and Hermès
    Salceda. 2015. <span>“<span>Trous</span> Du Livre, Plénitude Du Sens
    ?”</span> <em>Revue Formules, Presses Universitaires Du Nouveau
    Monde</em> Formes : Supports/Espaces (19).
    </div>
    </div>
    ```

    * Example error (HTTP code = 400):

    ```string
    La génération de la prévisualisation a échoué.
    ```
    """
    bibliography_style = request.form.get("bibliography_style", "chicagomodified")
    excerpt = request.form.get("excerpt", "").strip()
    if not excerpt:
        return "Bibliographie vide.", http.HTTPStatus.OK
    try:
        response = pandocapi.bibliography(
            excerpt,
            bibliography_style,
            current_app.config["SE_STYLES_DIR"] / f"{bibliography_style}.csl",
        )
        return response.content.decode(), http.HTTPStatus.OK
    except httpx.HTTPError:
        return (
            "La génération de la prévisualisation a échoué.",
            http.HTTPStatus.BAD_REQUEST,
        )


@blueprint.route("/article_preview", methods=("POST",))
def article_preview() -> Tuple[str, http.HTTPStatus]:
    """Convert an article content to HTML given yaml and bib metadata.

    This is a way to render an article for instant preview.

    * Route: `/api/article_preview`
    * Method: POST
    * Parameters:
        - `bibliography_style` (default: `chicagomodified`): the name/slug
          of the bibliographic style as defined by Zotero.
        - `md_content`: the string containing the content of the `.md` file.
        - `yaml_content`: the string containing the content of the `.yaml` file.
        - `bib_content`: the string containing the content of the `.bib` file.
    * Example response:

    ```html
    <article>
      <section id="introduction" class="level2">
      <h2>Introduction</h2>
      <p>Stylo est un éditeur de texte scientifique. Pour faire vos premiers
      pas sur Stylo, commencez par éditer cet article.</p>
    […]
    ```

    * Example error (HTTP code = 400):

    ```string
    La génération de la prévisualisation a échoué.
    ```
    """
    templates_folder = (Path() / "templates" / "generique").resolve()
    bibliography_style = request.form.get("bibliography_style", "chicagomodified")
    md_content = request.form.get("md_content", "")
    yaml_content = request.form.get("yaml_content", "")
    bib_content = request.form.get("bib_content", "")
    template_file_path = templates_folder / "templateHtml5.html5"
    csl_file_path = current_app.config["SE_STYLES_DIR"] / f"{bibliography_style}.csl"
    try:
        response = pandocapi.html_preview(
            md_content,
            yaml_content,
            bib_content,
            template_file_path,
            csl_file_path,
            bibliography_style,
        )
        return response.content.decode(), http.HTTPStatus.OK
    except httpx.HTTPError:
        return (
            "La génération de la prévisualisation a échoué.",
            http.HTTPStatus.BAD_REQUEST,
        )
