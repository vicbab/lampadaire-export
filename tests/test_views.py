from http import HTTPStatus
from pathlib import Path

import httpx
import pytest

from styloexport.utils import get_env_var

SE_PANDOC_API_BASE_URL = get_env_var("SE_PANDOC_API_BASE_URL")


def test_index(client, context):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert context[0]["form"].errors == {}
    assert "Sens public" in response.get_data(as_text=True)
    assert "Poursuivre" in response.get_data(as_text=True)


def test_index_submission(client, context):
    response = client.post("/", data={"edition": "sens-public"})
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "/sens-public/"


def test_edition(client, context):
    response = client.get("/sens-public/")
    assert response.status_code == HTTPStatus.OK
    assert context[0]["form"].errors == {}
    assert "stylo.huma-num.fr" in response.get_data(as_text=True)
    assert "Type d’export" in response.get_data(as_text=True)
    assert "Nom de votre export" in response.get_data(as_text=True)
    assert "Domaine de votre article" in response.get_data(as_text=True)
    assert "ID de votre article" in response.get_data(as_text=True)
    assert "Avec une Table des Matières (TOC)" in response.get_data(as_text=True)
    assert "Récupérer" in response.get_data(as_text=True)


def test_edition_generic_submission(client, context):
    response = client.post(
        "/generique/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "stylo.huma-num.fr",
            "article_id": "60db23ed66d232001371ac07",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/generique/article/stylo.huma-num.fr/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=0&with_ascii=0"
    )


def test_edition_localhost_submission(client, context):
    response = client.post(
        "/generique/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "localhost:3000",
            "article_id": "60db23ed66d232001371ac07",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/generique/article/localhost:3000/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=0&with_ascii=0"
    )


def test_edition_revue_submission(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "stylo.huma-num.fr",
            "article_id": "60db23ed66d232001371ac07",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/sens-public/article/stylo.huma-num.fr/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=0&with_ascii=0"
    )


def test_edition_submission_with_toc(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "stylo.huma-num.fr",
            "article_id": "60db23ed66d232001371ac07",
            "with_toc": True,
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/sens-public/article/stylo.huma-num.fr/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=1&with_ascii=0"
    )


def test_edition_submission_with_ascii(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "stylo.huma-num.fr",
            "article_id": "60db23ed66d232001371ac07",
            "with_ascii": True,
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/sens-public/article/stylo.huma-num.fr/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=0&with_ascii=1"
    )


def test_edition_submission_with_extra_spaces(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "  Titre article  ",
            "kind": "article",
            "domain": "stylo.huma-num.fr",
            "article_id": "    60db23ed66d232001371ac07  ",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == (
        "/sens-public/article/stylo.huma-num.fr/60db23ed66d232001371ac07/Titre-article/"
        "?with_toc=0&with_ascii=0"
    )


def test_edition_submission_with_bad_domain(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "example.com",
            "article_id": "60db23ed66d232001371ac07",
        },
    )
    assert context[0]["form"].errors == {"domain": ["Not a valid choice."]}
    assert response.status_code == HTTPStatus.OK


def test_edition_submission_without_a_name(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "",
            "kind": "article",
            "domain": "localhost:3000",
            "article_id": "60db23ed66d232001371ac07",
        },
    )
    assert context[0]["form"].errors == {"name": ["Veuillez saisir un nom."]}
    assert response.status_code == HTTPStatus.OK


def test_edition_submission_without_an_id(client, context):
    response = client.post(
        "/sens-public/",
        data={
            "name": "Titre article",
            "kind": "article",
            "domain": "localhost:3000",
            "article_id": "",
        },
    )
    assert context[0]["form"].errors == {
        "article_id": ["Il est nécessaire de soumettre un ID."]
    }
    assert response.status_code == HTTPStatus.OK


def test_edition_submission_without_data(client, context):
    response = client.post("/sens-public/", data={})
    assert response.status_code == HTTPStatus.OK
    assert context[0]["form"].errors == {
        "name": ["Veuillez saisir un nom."],
        "article_id": ["Il est nécessaire de soumettre un ID."],
        "domain": ["Il est nécessaire de choisir le domaine."],
        "kind": ["Il est nécessaire de choisir un type."],
    }
    assert "Nom de votre export" in response.get_data(as_text=True)
    assert "ID de votre article" in response.get_data(as_text=True)
    assert "Récupérer" in response.get_data(as_text=True)


def test_article_generique(client, context, httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        headers={"content-type": "image/png"},
    )
    response = client.get(
        "/generique/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].domain == "stylo.huma-num.fr"
    assert context[0]["article"].slug == "test"
    assert context[0]["article"].id == "5e32d54e4f58270018f9d251"
    assert context[0]["article"].versions == []
    assert len(context[0]["form"].formats.choices) == 10
    assert len(context[0]["form"].bibliography_style.choices) == 183
    assert context[0]["form"].version.choices == [("", "Version la plus récente")]
    assert (
        context[0]["bibliography_preview"]
        == "La génération de la prévisualisation a échoué."
    )
    assert context[0]["article"].errors == []
    assert str(next(iter(tmp_path.iterdir()))).endswith("generique")
    assert (
        len(
            list(
                (
                    tmp_path
                    / "generique"
                    / "stylo-huma-num-fr"
                    / "test-5e32d54e4f58270018f9d251"
                    / "originals"
                ).iterdir()
            )
        )
        == 3
    )
    assert (
        len(
            list(
                (
                    tmp_path
                    / "generique"
                    / "stylo-huma-num-fr"
                    / "test-5e32d54e4f58270018f9d251"
                    / "images"
                ).iterdir()
            )
        )
        == 1
    )


def test_article_generique_with_versions(client, context, httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_with_versions.graphql"
        ).read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        headers={"content-type": "image/png"},
    )
    response = client.get(
        "/generique/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].domain == "stylo.huma-num.fr"
    assert context[0]["article"].slug == "test"
    assert context[0]["article"].id == "5e32d54e4f58270018f9d251"
    assert len(context[0]["form"].version.choices) == 5
    assert context[0]["form"].version.choices == [
        ("", "Version la plus récente"),
        ("642482e90c166d001197d455", "Version sans nom - 2.0"),
        ("642482da0c166d001197d442", "Grosse version - 1.0"),
        ("642482c60c166d001197d421", "petite version - 0.1"),
        ("5e3392834f58270018f9d2b4", "Genesis - 0.0"),
    ]


def test_article_generique_without_images_or_bibliography(
    client, context, httpx_mock, tmp_path
):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path()
            / "tests"
            / "fixtures"
            / "How_to_Stylo_without_images_or_bibliography.graphql"
        ).read_text(),
    )
    response = client.get(
        "/generique/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].domain == "stylo.huma-num.fr"
    assert context[0]["article"].slug == "test"
    assert context[0]["article"].id == "5e32d54e4f58270018f9d251"
    assert context[0]["article"].errors == []
    assert str(next(iter(tmp_path.iterdir()))).endswith("generique")
    assert not (
        tmp_path
        / "generique"
        / "stylo-huma-num-fr"
        / "test-5e32d54e4f58270018f9d251"
        / "images"
    ).exists()


def test_article_generique_with_bibliography(client, context, httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        headers={"content-type": "image/png"},
    )
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=bibliography.html&with_toc=false&with_ascii=false&standalone=false"
        ),
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_bibliography.html"
        ).read_bytes(),
    )
    response = client.get(
        "/generique/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        context[0]["bibliography_excerpt"]
        == """
@book{goody_raison_1979,
  series = {Le sens commun},
  title = {La {Raison} graphique. {La} domestication de la pensée sauvage.},
  publisher = {Les Editions de Minuit},
  author = {Goody, Jack},
  year = {1979},
}"""
    )
    assert (
        context[0]["bibliography_preview"]
        == """<div id="refs" class="references csl-bib-body hanging-indent"
role="doc-bibliography">
<div id="ref-goody_raison_1979" class="csl-entry"
role="doc-biblioentry">
Goody, Jack. 1979. <em>La <span>Raison</span> graphique.
<span>La</span> domestication de la pensée sauvage.</em> Le sens
commun. Les Editions de Minuit.
</div>
</div>
"""
    )
    assert context[0]["article"].errors == []


def test_article_sens_public(client, context, httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        headers={"content-type": "image/png"},
    )
    response = client.get(
        "/sens-public/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].domain == "stylo.huma-num.fr"
    assert context[0]["article"].slug == "test"
    assert context[0]["article"].id == "5e32d54e4f58270018f9d251"
    assert context[0]["bibliography_excerpt"] == ""
    assert context[0]["bibliography_preview"] == ""
    assert context[0]["article"].errors == []
    assert str(next(iter(tmp_path.iterdir()))).endswith("sens-public")
    assert (
        len(
            list(
                (
                    tmp_path
                    / "sens-public"
                    / "stylo-huma-num-fr"
                    / "test-5e32d54e4f58270018f9d251"
                    / "originals"
                ).iterdir()
            )
        )
        == 3
    )
    assert (
        len(
            list(
                (
                    tmp_path
                    / "sens-public"
                    / "stylo-huma-num-fr"
                    / "test-5e32d54e4f58270018f9d251"
                    / "media"
                ).iterdir()
            )
        )
        == 3  # 1 image + 2 media from template.
    )


def test_article_with_404(client, context, httpx_mock):
    httpx_mock.add_response(url="https://stylo.huma-num.fr/graphql", status_code=404)
    response = client.get(
        "/sens-public/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
    )
    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].errors == [
        """
Client error '404 Not Found' for url 'https://stylo.huma-num.fr/graphql'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
    """.strip()
    ]


def test_article_with_503_from_stylo(client, context, httpx_mock):
    httpx_mock.add_exception(httpx.RequestError("Unable to access Stylo API."))
    with pytest.raises(httpx.RequestError):
        client.get(
            "/sens-public/article/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
        )


def test_downloads(client, tmp_path):
    (
        tmp_path / "sens-public" / "stylo.huma-num.fr" / "test-60db23ed66d232001371ac07"
    ).mkdir(parents=True)
    (
        tmp_path
        / "sens-public"
        / "stylo.huma-num.fr"
        / "test-60db23ed66d232001371ac07"
        / "test-60db23ed66d232001371ac07.md"
    ).write_text("content")
    response = client.get(
        (
            "/sens-public/downloads/stylo.huma-num.fr"
            "/60db23ed66d232001371ac07/test/test-60db23ed66d232001371ac07.md"
        )
    )
    assert response.status_code == HTTPStatus.OK
    assert response.content_length == len("content")


def test_downloads_inexisting_file(client, tmp_path):
    response = client.get(
        (
            "/sens-public/downloads/stylo.huma-num.fr"
            "/60db23ed66d232001371ac07/test/test-60db23ed66d232001371ac07.md"
        )
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
