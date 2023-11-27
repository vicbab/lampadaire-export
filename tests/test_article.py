import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from styloexport.article import Article
from styloexport.config import SE_EDITIONS
from styloexport.utils import get_env_var

SE_PANDOC_API_BASE_URL = get_env_var("SE_PANDOC_API_BASE_URL")


def test_article_generique(httpx_mock, tmp_path):
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

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.edition == "generique"
    assert article.domain == "stylo.huma-num.fr"
    assert article.slug == "test"
    assert article.id == "5e32d54e4f58270018f9d251"
    assert article.errors == []
    assert article.versions == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "config_path": "images",
            "name": "test-7dc926ed4014a96a908e5fb21de52329",
            "title": "",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        },
    ]
    assert str(next(iter(tmp_path.iterdir()))).endswith("generique")
    generated_files = sorted(
        list(
            (
                tmp_path
                / "generique"
                / "stylo-huma-num-fr"
                / "test-5e32d54e4f58270018f9d251"
            ).iterdir()
        )
    )
    assert str(generated_files[0]).endswith("images")
    assert str(generated_files[1]).endswith("images.zip")
    assert str(generated_files[2]).endswith("originals")
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
        == 3  # md + bib + yaml.
    )


def test_article_with_versions(httpx_mock, tmp_path):
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
    httpx_mock.add_response(
        url=(
            f"{SE_PANDOC_API_BASE_URL}convert/html/"
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert len(article.versions) == 4
    # The default version is the latest.
    article.export("", ["originals", "html"], "chicagomodified", templates_folder)
    md_generated = (
        tmp_path
        / "generique"
        / "stylo-huma-num-fr"
        / "test-5e32d54e4f58270018f9d251"
        / "test.md"
    )
    assert "## Introduction major version, no label\n\n" in md_generated.read_text()

    # You can export a chosen version.
    article.export(
        "642482da0c166d001197d442",
        ["originals", "html"],
        "chicagomodified",
        templates_folder,
    )
    md_generated = (
        tmp_path
        / "generique"
        / "stylo-huma-num-fr"
        / "test-5e32d54e4f58270018f9d251"
        / "test.md"
    )
    assert "## Introduction major version, with label\n\n" in md_generated.read_text()


def test_article_rewrite_youtube_iframe(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_youtube_iframe.graphql"
        ).read_text(),
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    article.export("", ["originals", "html"], "chicagomodified", templates_folder)
    md_generated = (
        tmp_path
        / "generique"
        / "stylo-huma-num-fr"
        / "test-5e32d54e4f58270018f9d251"
        / "test.md"
    )
    assert (
        "allowfullscreen>"
        in (
            Path() / "tests" / "fixtures" / "How_to_Stylo_youtube_iframe.graphql"
        ).read_text()
    )
    assert 'allowfullscreen="allowfullscreen">' in md_generated.read_text()


def test_article_generique_no_bibliography_in_yaml(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path()
            / "tests"
            / "fixtures"
            / "How_to_Stylo_no_bibliography_in_yaml.graphql"
        ).read_text(),
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    article.export("", ["originals", "html"], "chicagomodified", templates_folder)
    yaml_generated = (
        tmp_path
        / "generique"
        / "stylo-huma-num-fr"
        / "test-5e32d54e4f58270018f9d251"
        / "test.yaml"
    )
    assert "bibliography: test.bib" in yaml_generated.read_text()


def test_article_sens_public(httpx_mock, tmp_path):
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

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.edition == "sens-public"
    assert article.domain == "stylo.huma-num.fr"
    assert article.slug == "test"
    assert article.id == "5e32d54e4f58270018f9d251"
    assert article.errors == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "config_path": "media",
            "name": "test-7dc926ed4014a96a908e5fb21de52329",
            "title": "",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        },
    ]
    assert str(next(iter(tmp_path.iterdir()))).endswith("sens-public")
    generated_files = sorted(
        list(
            (
                tmp_path
                / "sens-public"
                / "stylo-huma-num-fr"
                / "test-5e32d54e4f58270018f9d251"
            ).iterdir()
        )
    )
    assert str(generated_files[0]).endswith("images.zip")
    assert ZipFile(generated_files[0]).namelist() == [
        "media/test-7dc926ed4014a96a908e5fb21de52329",
        "media/crochets.png",
        "media/logo.png",
    ]
    assert str(generated_files[1]).endswith("media")
    assert str(generated_files[2]).endswith("originals")
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
        == 3  # md + bib + yaml.
    )


def test_article_sens_public_without_images_contains_media(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path()
            / "tests"
            / "fixtures"
            / "How_to_Stylo_without_images_or_bibliography.graphql"
        ).read_text(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.edition == "sens-public"
    assert article.domain == "stylo.huma-num.fr"
    assert article.slug == "test"
    assert article.id == "5e32d54e4f58270018f9d251"
    assert article.errors == []
    assert article.images == []
    assert str(next(iter(tmp_path.iterdir()))).endswith("sens-public")
    generated_files = sorted(
        list(
            (
                tmp_path
                / "sens-public"
                / "stylo-huma-num-fr"
                / "test-5e32d54e4f58270018f9d251"
            ).iterdir()
        )
    )
    assert str(generated_files[0]).endswith("images.zip")
    assert ZipFile(generated_files[0]).namelist() == [
        "media/crochets.png",
        "media/logo.png",
    ]
    assert str(generated_files[1]).endswith("media")
    assert str(generated_files[2]).endswith("originals")
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
        == 3  # md + bib + yaml.
    )


@pytest.mark.skip(reason="Do we still want images in a particular folder?")
def test_article_with_images_metopes(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
    )

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
            "title": "",
            "name": "test-7dc926ed4014a96a908e5fb21de52329",
            "config_path": "icono/br",
        }
    ]


def test_article_with_images_without_extensions_ct_takes_precendence(
    httpx_mock, tmp_path
):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        # Here we force the jpg content type header.
        headers={"content-type": "image/jpeg"},
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [".png", ".jpg"],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
            "title": "",
            # Here we have the forced extension from content-type.
            "name": "test-7dc926ed4014a96a908e5fb21de52329.jpg",
            "config_path": "media",
        }
    ]


def test_article_with_images_with_extensions_ct_takes_precedence(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path()
            / "tests"
            / "fixtures"
            / "How_to_Stylo_images_with_extensions.graphql"
        ).read_text(),
    )
    httpx_mock.add_response(
        url="https://i.imgur.com/LkMTuKM.png",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        # Here we force the jpg content type header.
        headers={"content-type": "image/jpeg"},
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [".png", ".jpg"],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "url": "https://i.imgur.com/LkMTuKM.png",
            "title": "",
            # Here we have the forced extension from content-type.
            "name": "test-d8a934cf916c31ef6078339cce897ecb.jpg",
            "config_path": "media",
        }
    ]


def test_article_with_images_ct_does_not_take_precedence_if_extension_not_allowed(
    httpx_mock, tmp_path
):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path()
            / "tests"
            / "fixtures"
            / "How_to_Stylo_images_with_extensions.graphql"
        ).read_text(),
    )
    httpx_mock.add_response(
        url="https://i.imgur.com/LkMTuKM.png",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
        # Here we force the jpg content type header.
        headers={"content-type": "image/jpeg"},
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        # We do not accept anymore jpeg extension.
        [".png"],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == []
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "url": "https://i.imgur.com/LkMTuKM.png",
            "title": "",
            # Here we keep the original extension even with custom content-type.
            "name": "test-d8a934cf916c31ef6078339cce897ecb.png",
            "config_path": "media",
        }
    ]


def test_article_missing_images(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        status_code=404,
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == [
        """
Client error '404 Not Found' for url \
'https://avatars2.githubusercontent.com/u/16691667?s=200&v=4'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
    """.strip()
    ]
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
            "title": "",
            "name": "test-7dc926ed4014a96a908e5fb21de52329",
            "config_path": "media",
        }
    ]


def test_article_follow_image_redirect(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_image_redirect.graphql"
        ).read_text(),
    )
    httpx_mock.add_response(
        url="https://github.com/ecrituresnumeriques.png",
        status_code=302,
        headers={
            "location": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4"
        },
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)
    requests = httpx_mock.get_requests()
    assert len(requests) == 3  # graphql + initial image url + redirect.
    assert article.images == [
        {
            "alt": "Titre de mon image",
            "config_path": "media",
            "name": "test-7dc926ed4014a96a908e5fb21de52329",
            "original_url": "https://github.com/ecrituresnumeriques.png",
            "title": "",
            "url": "https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        },
    ]


def test_article_no_redownload_images(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    # Again.
    article.download_images(templates_folder)
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_article_redownload_images_if_forced(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.graphql").read_text(),
    )
    httpx_mock.add_response(
        url="https://avatars2.githubusercontent.com/u/16691667?s=200&v=4",
        content=(
            Path() / "tests" / "fixtures" / "7dc926ed4014a96a908e5fb21de52329"
        ).read_bytes(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    # Again.
    article.download_images(templates_folder, force=True)
    requests = httpx_mock.get_requests()
    assert len(requests) == 3


def test_article_bad_instance(httpx_mock, tmp_path):
    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "example.com",
        "60db23ed66d232001371ac07",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == ["Stylo instance not supported."]
    assert len(list(tmp_path.iterdir())) == 0


def test_article_bad_edition(httpx_mock, tmp_path):
    article = Article(
        "sens-privé",
        {},
        "stylo.huma-num.fr",
        "60db23ed66d232001371ac07",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == ["Stylo edition not supported."]
    assert len(list(tmp_path.iterdir())) == 0


def test_article_with_empty_yaml(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo_without_yaml.graphql"
        ).read_text(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == ["YAML file is empty."]


def test_article_with_404(httpx_mock, tmp_path):
    httpx_mock.add_response(url="https://stylo.huma-num.fr/graphql", status_code=404)

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == [
        """
Client error '404 Not Found' for url 'https://stylo.huma-num.fr/graphql'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
    """.strip()
    ]


def test_article_unknown(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://stylo.huma-num.fr/graphql",
        content=(
            Path() / "tests" / "fixtures" / "error_article_not_found.graphql"
        ).read_text(),
    )

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "60db23ed66d232001371ac07",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)

    assert article.errors == ["Unable to find article with id 60db23ed66d232001371ac07"]


def test_article_generique_all_export(app, httpx_mock, tmp_path, mocker):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=(f"{SE_PANDOC_API_BASE_URL}convert/tex/?name=test.tex&with_toc=false"),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.tex").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/tei/?name=test-tei.xml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo-tei.xml").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/erudit/?name=test-erudit.xml",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo-erudit.xml"
        ).read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=false",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.pdf").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/odt/?name=test.odt&with_toc=false",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.odt").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/docx/?name=test.docx&with_toc=false",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.docx").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/icml/?name=test.icml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.icml").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/tei/?name=test-metopes-tei.xml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo-tei.xml").read_bytes(),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        [
            "originals",
            "html",
            "tex",
            "pdf",
            "odt",
            "docx",
            "icml",
            "xml-tei",
            "xml-erudit",
            "xml-tei-metopes",
        ],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    # image archive + md + bib + yaml + html + tex + image + pdf + odt + docx
    # + icml + xml-tei + xml-erudit + xml-tei-metopes
    assert zipfile_write.call_count == 14


def test_article_generique_only_html(app, httpx_mock, tmp_path, mocker):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        ["originals", "html"],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    assert zipfile_write.call_count == 6  # md + bib + yaml + images + html

def test_article_lampadaire_pdf(app, httpx_mock, tmp_path, mocker):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/tei/?name=test-tei.xml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo-tei.xml").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/erudit/?name=test-erudit.xml",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo-erudit.xml"
        ).read_bytes(),
    )
    httpx_mock.add_response(
        url=(f"{SE_PANDOC_API_BASE_URL}convert/tex/?name=test.tex&with_toc=false"),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.tex").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=false",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.pdf").read_bytes(),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "lampadaire",
        SE_EDITIONS["lampadaire"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["lampadaire"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "lampadaire").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        [
            "pdf",
        ],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    # one image + twice two images from templates (crochets + logo sens-public)
    # + md + bib + yaml + html
    # + pdf + tex + xml-tei + xml-erudit
    assert zipfile_write.call_count == 5

def test_article_sens_public_all_export(app, httpx_mock, tmp_path, mocker):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/tei/?name=test-tei.xml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo-tei.xml").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/erudit/?name=test-erudit.xml",
        content=(
            Path() / "tests" / "fixtures" / "How_to_Stylo-erudit.xml"
        ).read_bytes(),
    )
    httpx_mock.add_response(
        url=(f"{SE_PANDOC_API_BASE_URL}convert/tex/?name=test.tex&with_toc=false"),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.tex").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=false",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.pdf").read_bytes(),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "sens-public",
        SE_EDITIONS["sens-public"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["sens-public"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "sens-public").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        [
            "originals",
            "html",
            "tex",
            "pdf",
            "xml-tei",
            "xml-erudit",
        ],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    # one image + twice two images from templates (crochets + logo sens-public)
    # + md + bib + yaml + html
    # + pdf + tex + xml-tei + xml-erudit
    assert zipfile_write.call_count == 14


def test_article_metopes_export(app, httpx_mock, tmp_path, mocker):
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
        url=f"{SE_PANDOC_API_BASE_URL}convert/xml/tei/?name=test-metopes-tei.xml",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo-tei.xml").read_bytes(),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "", ["originals", "xml-tei-metopes"], "chicagomodified", templates_folder
    )

    assert export_file_path.exists()
    assert (
        zipfile_write.call_count == 6
    )  # md + bib + yaml + images + xml-tei-metopes + one image


def test_article_generique_export_with_pdf_template_error(
    app, httpx_mock, tmp_path, mocker
):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=false",
        status_code=422,
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        ["originals", "html", "pdf"],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    # image archive + md + bib + yaml + html + pdf
    assert zipfile_write.call_count == 6
    assert article.errors == [
        "Erreur pendant la génération de « How to Stylo » (convert/pdf/)"
    ]


def test_article_generique_export_with_name_length_error(
    app, httpx_mock, tmp_path, mocker
):
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
            "?name=a.html&with_toc=false&with_ascii=false"
        ),
        status_code=422,
        json={
            "detail": [
                {
                    "ctx": {"limit_value": 8},
                    "loc": ["query", "name"],
                    "msg": "ensure this value has at least 8 characters",
                    "type": "value_error.any_str.min_length",
                }
            ]
        },
    )

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "a",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        ["originals", "html"],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    assert article.errors == [
        (
            "Erreur pendant la génération de « How to Stylo » "
            "(convert/html/)\xa0: [{'ctx': {'limit_value': 8}, "
            "'loc': ['query', 'name'], "
            "'msg': 'ensure this value has at least 8 characters', "
            "'type': 'value_error.any_str.min_length'}]"
        )
    ]


def test_article_generique_export_with_pdf_pandoc_error(
    app, httpx_mock, tmp_path, mocker
):
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
            "?name=test.html&with_toc=false&with_ascii=false"
        ),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=false",
        status_code=500,
        content=json.dumps({"detail": "Pandoc error"}),
    )
    zipfile_write = mocker.patch("styloexport.article.ZipFile.write")
    zipfile_write.return_value = "dummy"

    article = Article(
        "generique",
        SE_EDITIONS["generique"],
        "stylo.huma-num.fr",
        "5e32d54e4f58270018f9d251",
        "test",
        "",
        tmp_path,
        ["generique"],
        ["https://stylo.huma-num.fr"],
        [".png"],
    )
    templates_folder = (Path() / "templates" / "generique").resolve()
    article.fetch_all(templates_folder)
    export_file_path = article.export(
        "",
        ["originals", "html", "pdf"],
        "chicagomodified",
        templates_folder,
    )

    assert export_file_path.exists()
    # image archive + md + bib + yaml + html + pdf
    assert zipfile_write.call_count == 6
    assert article.errors == [
        (
            "Erreur pendant la génération de « How to Stylo » "
            "(convert/pdf/) : Pandoc error"
        )
    ]
