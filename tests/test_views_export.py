from http import HTTPStatus
from pathlib import Path

from styloexport.utils import get_env_var

SE_PANDOC_API_BASE_URL = get_env_var("SE_PANDOC_API_BASE_URL")


def test_export_generique_all(app, client, context, httpx_mock, tmp_path):
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

    formats = (
        "formats=originals&formats=html&formats=tex&formats=pdf&formats=odt"
        "&formats=docx"
    )
    formats_xml = (
        "formats=icml&formats=xml-tei&formats=xml-erudit&formats=xml-tei-metopes"
    )
    response = client.get(
        (
            "/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&{formats_xml}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "docx-html-icml-odt-originals-pdf-tex"
    formats_xml = "xml-erudit-xml-tei-xml-tei-metopes"
    filename = (
        f"test-5e32d54e4f58270018f9d251--{formats}-{formats_xml}-toc-0-ascii-0.zip"
    )
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_generique_all_with_error_from_pandoc(
    app, client, context, httpx_mock, tmp_path
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
    formats = (
        "formats=originals&formats=html&formats=tex&formats=pdf&formats=odt"
        "&formats=docx"
    )
    formats_xml = (
        "formats=icml&formats=xml-tei&formats=xml-erudit&formats=xml-tei-metopes"
    )
    response = client.get(
        (
            "/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/a/"
            f"?{formats}&{formats_xml}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert context[0]["article"].errors == [
        (
            "Erreur pendant la génération de «\xa0How to Stylo\xa0» "
            "(convert/html/)\xa0: "
            "[{'ctx': {'limit_value': 8}, 'loc': ['query', 'name'], "
            "'msg': 'ensure this value has at least 8 characters', "
            "'type': 'value_error.any_str.min_length'}]"
        )
    ]


def test_export_generique_all_with_version(app, client, context, httpx_mock, tmp_path):
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

    formats = (
        "formats=originals&formats=html&formats=tex&formats=pdf&formats=odt"
        "&formats=docx"
    )
    formats_xml = (
        "formats=icml&formats=xml-tei&formats=xml-erudit&formats=xml-tei-metopes"
    )
    response = client.get(
        (
            "/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&{formats_xml}&bibliography_style=chicagomodified"
            "&version=642482da0c166d001197d442"
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "docx-html-icml-odt-originals-pdf-tex"
    formats_xml = "xml-erudit-xml-tei-xml-tei-metopes"
    filename = (
        f"test-5e32d54e4f58270018f9d251-642482da0c166d001197d442-"
        f"{formats}-{formats_xml}-toc-0-ascii-0.zip"
    )
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_generique_all_with_empty_version(
    app, client, context, httpx_mock, tmp_path
):
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

    formats = (
        "formats=originals&formats=html&formats=tex&formats=pdf&formats=odt"
        "&formats=docx"
    )
    formats_xml = (
        "formats=icml&formats=xml-tei&formats=xml-erudit&formats=xml-tei-metopes"
    )
    response = client.get(
        (
            "/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&{formats_xml}&bibliography_style=chicagomodified"
            "&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "docx-html-icml-odt-originals-pdf-tex"
    formats_xml = "xml-erudit-xml-tei-xml-tei-metopes"
    filename = (
        f"test-5e32d54e4f58270018f9d251--{formats}-{formats_xml}-toc-0-ascii-0.zip"
    )
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_generique_all_without_version(
    app, client, context, httpx_mock, tmp_path
):
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

    formats = (
        "formats=originals&formats=html&formats=tex&formats=pdf&formats=odt"
        "&formats=docx"
    )
    formats_xml = (
        "formats=icml&formats=xml-tei&formats=xml-erudit&formats=xml-tei-metopes"
    )
    response = client.get(
        (
            "/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&{formats_xml}&bibliography_style=chicagomodified"
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert context[0]["form"].errors == {
        "version": [
            "Not a valid choice.",
            (
                "Version incorrecte, choix possibles : , 642482e90c166d001197d455, "
                "642482da0c166d001197d442, 642482c60c166d001197d421, "
                "5e3392834f58270018f9d2b4."
            ),
        ]
    }


def test_export_generique_html_only(app, client, context, httpx_mock, tmp_path):
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

    formats = "formats=html"
    response = client.get(
        (
            f"/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    filename = "test-5e32d54e4f58270018f9d251--html-toc-0-ascii-0.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"

def test_export_lampadaire_pdf(app, client, context, httpx_mock, tmp_path):
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

    formats = "formats=pdf"
    response = client.get(
        (
            f"/lampadaire/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "pdf"
    filename = f"test-5e32d54e4f58270018f9d251--{formats}-toc-0-ascii-0.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_sens_public_all(app, client, context, httpx_mock, tmp_path):
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

    formats = "formats=all"
    response = client.get(
        (
            f"/sens-public/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "html-originals-pdf-tex-xml-erudit-xml-tei"
    filename = f"test-5e32d54e4f58270018f9d251--{formats}-toc-0-ascii-0.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_sens_public_all_with_toc(app, client, context, httpx_mock, tmp_path):
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
            "?name=test.html&with_toc=true&with_ascii=false"
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
        url=(f"{SE_PANDOC_API_BASE_URL}convert/tex/?name=test.tex&with_toc=true"),
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.tex").read_bytes(),
    )
    httpx_mock.add_response(
        url=f"{SE_PANDOC_API_BASE_URL}convert/pdf/?name=test.pdf&with_toc=true",
        content=(Path() / "tests" / "fixtures" / "How_to_Stylo.pdf").read_bytes(),
    )

    formats = "formats=all"
    response = client.get(
        (
            "/sens-public/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&with_toc=1&with_ascii=0&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "html-originals-pdf-tex-xml-erudit-xml-tei"
    filename = f"test-5e32d54e4f58270018f9d251--{formats}-toc-1-ascii-0.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_sens_public_all_with_ascii(app, client, context, httpx_mock, tmp_path):
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
            "?name=test.html&with_toc=false&with_ascii=true"
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

    formats = "formats=all"
    response = client.get(
        (
            "/sens-public/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&with_toc=0&with_ascii=1&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "html-originals-pdf-tex-xml-erudit-xml-tei"
    filename = f"test-5e32d54e4f58270018f9d251--{formats}-toc-0-ascii-1.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_metopes(app, client, context, httpx_mock, tmp_path):
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

    formats = "formats=xml-tei-metopes"
    response = client.get(
        (
            f"/generique/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            f"?{formats}&bibliography_style=chicagomodified&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    formats = "xml-tei-metopes"
    filename = f"test-5e32d54e4f58270018f9d251--{formats}-toc-0-ascii-0.zip"
    assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"


def test_export_unsupported_format(client, context, httpx_mock, tmp_path):
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

    response = client.get(
        (
            "/sens-public/export/stylo.huma-num.fr/5e32d54e4f58270018f9d251/test/"
            "?formats=unsupported_format&version="
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert context[0]["form"].errors == {"formats": ["Not a valid choice."]}
