import json
from pathlib import Path

import httpx

from .utils import get_env_var

SE_PANDOC_API_BASE_URL = get_env_var("SE_PANDOC_API_BASE_URL")
SE_PANDOC_API_TIMEOUT = get_env_var("SE_PANDOC_API_TIMEOUT")


def call_pandocapi(url: str, params: dict, files: dict) -> httpx.Response:
    timeout = httpx.Timeout(SE_PANDOC_API_TIMEOUT)
    with httpx.Client(base_url=SE_PANDOC_API_BASE_URL, timeout=timeout) as client:
        try:
            response = client.post(url, params=params, files=files)
            response.raise_for_status()
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            exc.url = url  # type: ignore[attr-defined]
            raise exc
        except httpx.HTTPStatusError as exc:
            try:
                json_response: dict = exc.response.json()
                exc.detail = json_response.get("detail")  # type: ignore[attr-defined]
                print(exc.detail)
            except json.decoder.JSONDecodeError:
                pass
            exc.url = url  # type: ignore[attr-defined]
            print(
                (
                    f"Error response {exc.response.status_code} "
                    f"while requesting {exc.request.url!r}."
                )
            )
            raise exc
    return response


class PandocAPI:
    def __init__(
        self, md_file_path: Path, yaml_file_path: Path, bib_file_path: Path
    ) -> None:
        self.md_file_path = md_file_path
        self.yaml_file_path = yaml_file_path
        self.bib_file_path = bib_file_path

    def bibliography(
        self, bibliography_excerpt: str, bibliography_style: str, csl_file_path: Path
    ) -> httpx.Response:
        params = {
            "name": "bibliography.html",
            "with_toc": "false",
            "with_ascii": "false",
            "standalone": "false",
        }
        files = {
            "markdown_file": ("input.md", ""),
            "bibtex_file": ("input.bib", bibliography_excerpt.encode('utf-8')),
            "yaml_file": ("input.yaml", "---\nnocite: '@*'\n---\n".encode('utf-8')),
            "csl_file": (f"{bibliography_style}.csl", csl_file_path.read_bytes().decode('latin-1').encode('utf-8')),
        }
        return call_pandocapi("convert/html/", params=params, files=files)

    def html_preview(
        self,
        md_content: str,
        yaml_content: str,
        bib_content: str,
        template_file_path: Path,
        csl_file_path: Path,
        bibliography_style: str,
    ) -> httpx.Response:
        params = {
            "name": "preview.html",
            "with_toc": "false",
            "with_ascii": "false",
            "standalone": "false",
        }
        files = {
            "markdown_file": ("input.md", md_content.decode('latin-1').encode('utf-8')),
            "bibtex_file": ("input.bib", bib_content.decode('utf-8').encode('utf-8')),
            "yaml_file": ("input.yaml", yaml_content.decode('latin-1').encode('utf-8')),
            "template_file": ("template.html", template_file_path.read_bytes().decode('utf-8').encode('utf-8')),
            "csl_file": (f"{bibliography_style}.csl", csl_file_path.read_bytes().decode('utf-8').encode('utf-8')),
        }
        return call_pandocapi("convert/html/", params=params, files=files)

    def html(
        self,
        export_file_name: str,
        template_file_path: Path,
        csl_file_path: Path,
        with_toc: bool,
        with_ascii: bool,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
            "with_toc": str(bool(with_toc)).lower(),
            "with_ascii": str(bool(with_ascii)).lower(),
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes().decode('latin-1')),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes().decode('latin-1')),
            "template_file": ("template.html", template_file_path.read_bytes().decode('latin-1')),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes().decode('latin-1')),
        }
        return call_pandocapi("convert/html/", params=params, files=files)

    def tex(
        self,
        export_file_name: str,
        template_file_path: Path,
        csl_file_path: Path,
        with_toc: bool,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
            "with_toc": str(bool(with_toc)).lower(),
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "template_file": ("template.html", template_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/tex/", params=params, files=files)

    def xml_tei(
        self,
        export_file_name: str,
        template_file_path: Path,
        csl_file_path: Path,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "template_file": ("template-tei.tei", template_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/xml/tei/", params=params, files=files)

    def xml_tei_metopes(
        self,
        export_file_name: str,
        template_file_path: Path,
        csl_file_path: Path,
        xsl_file_path: Path,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "template_file": ("template-tei.tei", template_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
            "xsl_file": ("template-metopes.xsl", xsl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/xml/tei/", params=params, files=files)

    def xml_erudit(
        self,
        export_file_name: str,
        template_file_path: Path,
        csl_file_path: Path,
        xsl_file_path: Path,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "template_file": ("template-xhtml.html", template_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
            "xsl_file": ("template-erudit.xsl", xsl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/xml/erudit/", params=params, files=files)

    def pdf(
        self,
        export_file_name: str,
        images_file_path: Path,
        template_file_path: Path,
        csl_file_path: Path,
        with_toc: bool,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
            "with_toc": str(bool(with_toc)).lower(),
            "verbosity": "INFO",
            "fail-if-warnings": "false",
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes().decode('latin-1').encode('utf-8')),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes().decode('latin-1').encode('utf-8')),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes().decode('latin-1').encode('utf-8')),
            "images_file": ("images.zip", images_file_path.read_bytes().decode('latin-1').encode('utf-8')),
            "template_file": ("templateLaTeX.latex", template_file_path.read_bytes().decode('utf-8').encode('utf-8')),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes().decode('latin-1').encode('utf-8')),
        }
        return call_pandocapi("convert/pdf/", params=params, files=files)

    def odt(
        self,
        export_file_name: str,
        images_file_path: Path,
        csl_file_path: Path,
        with_toc: bool,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
            "with_toc": str(bool(with_toc)).lower(),
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "images_file": ("images.zip", images_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/odt/", params=params, files=files)

    def docx(
        self,
        export_file_name: str,
        images_file_path: Path,
        csl_file_path: Path,
        with_toc: bool,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
            "with_toc": str(bool(with_toc)).lower(),
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "images_file": ("images.zip", images_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/docx/", params=params, files=files)

    def icml(
        self,
        export_file_name: str,
        images_file_path: Path,
        csl_file_path: Path,
        style_name: str,
    ) -> httpx.Response:
        params = {
            "name": export_file_name,
        }
        files = {
            "markdown_file": ("input.md", self.md_file_path.read_bytes()),
            "bibtex_file": ("input.bib", self.bib_file_path.read_bytes()),
            "yaml_file": ("input.yaml", self.yaml_file_path.read_bytes()),
            "images_file": ("images.zip", images_file_path.read_bytes()),
            "csl_file": (f"{style_name}.csl", csl_file_path.read_bytes()),
        }
        return call_pandocapi("convert/icml/", params=params, files=files)
