from http import HTTPStatus
from pathlib import Path

from styloexport.utils import get_env_var

SE_PANDOC_API_BASE_URL = get_env_var("SE_PANDOC_API_BASE_URL")


def test_api_available_exports(client, context):
    response = client.get("/api/available_exports")
    assert response.status_code == HTTPStatus.OK
    assert response.json == [
        {"key": "originals", "name": "fichiers originaux (md, yaml et bib)"},
        {"key": "html", "name": "conversion HTML"},
        {"key": "tex", "name": "conversion LaTeX"},
        {"key": "pdf", "name": "conversion PDF"},
        {"key": "odt", "name": "conversion ODT (OpenOffice)"},
        {"key": "docx", "name": "conversion DOCX (Word)"},
        {"key": "icml", "name": "conversion ICML (Impress)"},
        {"key": "xml-tei", "name": "conversion XML-TEI"},
        {"key": "xml-erudit", "name": "conversion XML Erudit"},
        {"key": "xml-tei-metopes", "name": "conversion XML-TEI Commons (Métopes)"},
    ]


def test_api_available_bibliographic_styles(client, context):
    response = client.get("/api/available_bibliographic_styles")
    assert response.status_code == HTTPStatus.OK
    assert response.json[0] == {
        "categories": {"fields": ["humanities"], "format": ""},
        "dependent": 1,
        "href": "https://www.zotero.org/styles/chicagomodified",
        "name": "chicagomodified",
        "title": "Chicago (modified)",
        "updated": "2022-12-20 00:00:00",
    }
    assert response.json[1] == {
        "categories": {"fields": ["humanities"], "format": "author-date"},
        "dependent": 0,
        "href": "https://www.zotero.org/styles/acme-an-international-journal-for-critical-geographies",
        "name": "acme-an-international-journal-for-critical-geographies",
        "title": "ACME: An International Journal for Critical Geographies",
        "updated": "2018-06-17 04:54:57",
    }
    assert len(response.json) == 183


def test_api_allowed_instance_base_urls(client, context):
    response = client.get("/api/allowed_instance_base_urls")
    assert response.status_code == HTTPStatus.OK
    assert response.json == ["https://stylo.huma-num.fr", "http://localhost:3000"]


def test_api_bibliography_preview(client, context, httpx_mock):
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=bibliography.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_bibliography.html"
        ).read_bytes(),
    )
    response = client.post(
        "/api/bibliography_preview",
        data={
            "bibliography_preview": "chicagomodified",
            "excerpt": """
@article{reggiani_2015,
    title = {{Trous} du livre, plénitude du sens ?},
    volume = {Formes : Supports/Espaces},
    number = {19},
    journal = {Revue Formules, Presses Universitaires du Nouveau Monde},
    author = {Reggiani, Christelle and Reig, Christophe and Thomas, \
Jean-Jacques and Salceda, Hermès},
    year = {2015}
}
        """,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.text.startswith(
        '<div id="refs" class="references csl-bib-body hanging-indent"'
    )


def test_api_bibliography_empty(client, context, httpx_mock):
    response = client.post(
        "/api/bibliography_preview",
        data={
            "bibliography_preview": "chicagomodified",
            "excerpt": "  ",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.text == "Bibliographie vide."


def test_api_bibliography_preview_status_not_found(client, context, httpx_mock):
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=bibliography.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        status_code=404,
    )
    response = client.post(
        "/api/bibliography_preview",
        data={
            "bibliography_preview": "chicagomodified",
            "excerpt": """
@article{reggiani_2015,
    title = {{Trous} du livre, plénitude du sens ?},
    volume = {Formes : Supports/Espaces},
    number = {19},
    journal = {Revue Formules, Presses Universitaires du Nouveau Monde},
    author = {Reggiani, Christelle and Reig, Christophe and Thomas, \
Jean-Jacques and Salceda, Hermès},
    year = {2015}
}
        """,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.text == "La génération de la prévisualisation a échoué."


def test_api_bibliography_preview_status_error(client, context, httpx_mock):
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=bibliography.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        status_code=500,
        json={"detail": "missing value in biblio"},
    )
    response = client.post(
        "/api/bibliography_preview",
        data={
            "bibliography_preview": "chicagomodified",
            "excerpt": """
@article{reggiani_2015,
    title = {{Trous} du livre, plénitude du sens ?},
    volume = {Formes : Supports/Espaces},
    number = {19},
    journal = {Revue Formules, Presses Universitaires du Nouveau Monde},
    author = {Reggiani, Christelle and Reig, Christophe and Thomas, \
Jean-Jacques and Salceda, Hermès},
    year = {2015}
}
        """,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.text == "La génération de la prévisualisation a échoué."


def test_api_article_preview(client, context, httpx_mock):
    fixtures_path = Path() / "tests" / "fixtures"
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=preview.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        content=(fixtures_path / "How_to_Stylo_preview.html").read_bytes(),
    )
    response = client.post(
        "/api/article_preview",
        data={
            "bibliography_style": "chicagomodified",
            "md_content": (fixtures_path / "How_to_Stylo.md").read_text(),
            "yaml_content": (fixtures_path / "How_to_Stylo.yaml").read_text(),
            "bib_content": (fixtures_path / "How_to_Stylo.bib").read_text(),
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.text.startswith(
        """\
<article>
  <section id="introduction" class="level2">
  <h2>Introduction</h2>
  <p>Stylo est un éditeur de texte scientifique. Pour faire vos premiers
  pas sur Stylo, commencez par éditer cet article.</p>"""
    )
    assert response.text.endswith(
        """\
  <ol>
  <li id="fn1" role="doc-endnote"><p>La note se trouve ensuite à la fin
  du texte.<a href="#fnref1" class="footnote-back"
  role="doc-backlink">↩︎</a></p></li>
  <li id="fn2" role="doc-endnote"><p>Voici une note déclarée en fin de
  document<a href="#fnref2" class="footnote-back"
  role="doc-backlink">↩︎</a></p></li>
  <li id="fn3" role="doc-endnote"><p>Une note déclarée “n’importe où”,
  ici, juste en dessous du paragraphe correspondant.<a href="#fnref3"
  class="footnote-back" role="doc-backlink">↩︎</a></p></li>
  <li id="fn4" role="doc-endnote"><p>Voici une note avec un label
  textuel.<a href="#fnref4" class="footnote-back"
  role="doc-backlink">↩︎</a></p></li>
  <li id="fn5" role="doc-endnote"><p>Ceci est une note de bas de page
  inline. Elle peut être aussi longue que vous voulez, elle sera
  transformée comme les autres en note de bas de page<a href="#fnref5"
  class="footnote-back" role="doc-backlink">↩︎</a></p></li>
  <li id="fn6" role="doc-endnote"><p>L’identifiant Orcid permettra de
  récupérer automatiquement l’affiliation et la biographie de
  l’auteur.<a href="#fnref6" class="footnote-back"
  role="doc-backlink">↩︎</a></p></li>
  </ol>
  </section>
  </article>
"""
    )


def test_api_article_preview_status_error(client, context, httpx_mock):
    fixtures_path = Path() / "tests" / "fixtures"
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=preview.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        status_code=404,
    )
    response = client.post(
        "/api/article_preview",
        data={
            "bibliography_style": "chicagomodified",
            "md_content": (fixtures_path / "How_to_Stylo.md").read_text(),
            "yaml_content": (fixtures_path / "How_to_Stylo.yaml").read_text(),
            "bib_content": (fixtures_path / "How_to_Stylo.bib").read_text(),
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.text == "La génération de la prévisualisation a échoué."
