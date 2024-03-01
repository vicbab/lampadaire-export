import hashlib
import mimetypes
import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse
from zipfile import ZipFile

import httpx
import wrapt
import yaml
from slugify import slugify

from .pandocapi import PandocAPI
from .styloapi import StyloAPI
from .utils import get_domain_from_url, get_env_var

MD_IMAGE_PATTERN = re.compile(
    r"""
    !\[                             # regular markdown image starter
    (?P<alt>.*?)                    # alternative text to the image
    \]\(                            # close alt text and start url
    (?P<url>.*?)                    # url of the image
    (?:\s*\"(?P<title>.*?)?\")?     # optional text to set a title
    \)                              # close of url-part parenthesis
    """,
    re.VERBOSE | re.MULTILINE,
)
SE_IMAGES_TIMEOUT = get_env_var("SE_IMAGES_TIMEOUT")


@wrapt.decorator
def bail_on_errors(wrapped: Callable, instance: Any, args: list, kwargs: dict) -> Any:
    """Decorator to stop processing an article which contains errors."""
    if instance.errors:
        return
    return wrapped(*args, **kwargs)


class Article:
    def __init__(
        self,
        edition: str,
        edition_configuration: dict,
        domain: str,
        id: str,
        slug: str,
        title: str,
        download_dir: Path,
        allowed_editions: List[str],
        allowed_base_urls: List[str],
        supported_images_extensions: List[str],
    ) -> None:
        self.edition = edition
        self.edition_configuration = edition_configuration
        self.domain = domain
        self.domain_slug = slugify(domain)
        self.id = id
        self.slug = slug
        self.title = title
        self.download_dir = download_dir / edition / self.domain_slug / f"{slug}-{id}"
        self.versions: List[Dict] = []
        self.errors: List[str] = []
        self.metadata: Dict[str, str] = {}
        self.images: List[Dict] = []
        self.allowed_base_urls = allowed_base_urls
        self._check_edition(allowed_editions)
        self._check_instance(allowed_base_urls)
        self.supported_images_extensions = supported_images_extensions

    @property
    def filenames(self) -> dict:
        return {
            "bib": f"{self.slug}.bib",
            "md": f"{self.slug}.md",
            "yaml": f"{self.slug}.yaml",
        }

    def _check_edition(self, allowed_editions: List[str]) -> None:
        if self.edition not in allowed_editions:
            self.errors.append("Stylo edition not supported.")

    def _check_instance(self, allowed_base_urls: List[str]) -> None:
        if self.domain not in [get_domain_from_url(url) for url in allowed_base_urls]:
            self.errors.append("Stylo instance not supported.")

    @bail_on_errors
    def get_stylo_data(self, version: str) -> Optional[dict]:
        urls = dict((get_domain_from_url(url), url) for url in self.allowed_base_urls)
        url = urls[self.domain]
        styloapi = StyloAPI(url)

        try:
            response = styloapi.article(self.id)
        except httpx.HTTPStatusError as e:
            self.errors.append(e.args[0])
            return None

        data: dict = response.json()
        if "errors" in data:
            for error in data["errors"]:
                self.errors.append(error["message"])
            return None

        article_data: dict = data["data"]["article"]
        if version:
            article_content: dict = [
                version_
                for version_ in article_data["versions"]
                if version_["_id"] == version
            ].pop()
        else:
            article_content = article_data["workingVersion"]

        self.title = self.title or article_data["title"]
        self.metadata["title"] = article_data["title"]
        self.versions = article_data["versions"]
        return article_content

    @bail_on_errors
    def save_files(self, stylo_data: dict) -> None:
        originals_download_dir = self.download_dir / "originals"
        if not originals_download_dir.exists():
            originals_download_dir.mkdir(parents=True, exist_ok=True)

        for kind, filename in self.filenames.items():
            (originals_download_dir / filename).write_text(stylo_data[kind])

    @bail_on_errors
    def extract_metadata(self) -> None:
        yaml_content = (
            self.download_dir / "originals" / self.filenames["yaml"]
        ).read_text()
        try:
            metadata = next(yaml.safe_load_all(yaml_content))
        except yaml.YAMLError as e:
            self.errors.append(f"{e.args[0]}: {e.args[2]}")
            return
        except StopIteration:
            self.errors.append("YAML file is empty.")
            return
        if not isinstance(metadata, dict):
            self.errors.append("YAML file is corrupted.")
            return

        self.metadata.update(metadata)
        abstracts = metadata.get("abstract", [])
        for abstract in abstracts:
            # TODO: fallback on English?
            if abstract["lang"] == "fr":
                self.metadata["abstract"] = abstract.get("text", "")
                break

    @bail_on_errors
    def extract_images(self) -> None:
        md_content = (
            self.download_dir / "originals" / self.filenames["md"]
        ).read_text()

        images = MD_IMAGE_PATTERN.findall(md_content)
        if images:
            for image in images:
                self.images.append(dict(zip(("alt", "url", "title"), image)))

    @bail_on_errors
    def download_images(self, templates_folder: Path, force: bool = False) -> None:
        zip_file_path = self.download_dir / "images.zip"
        images_config_path = self.edition_configuration.get("images_path", "images")
        # In case of Sens-Public for instance, we want to add
        # media referenced in the template with article's images.
        media_folder = templates_folder / images_config_path
        # print(str(images_config_path))
        if not self.images and not media_folder.exists():
            # We still want an empty archive to upload to the server.
            with ZipFile(zip_file_path, mode="w") as archive:
                return

        images_path = self.download_dir / images_config_path
        images_path.mkdir(parents=True, exist_ok=True)

        image_paths = []
        for image in self.images:
            image["config_path"] = images_config_path
            image_path = self._download_image(image, images_path, force)
            if image_path is not None:
                image_paths.append(image_path)

        with ZipFile(zip_file_path, mode="a") as archive:
            for image_path in image_paths:
                arcname = image_path.relative_to(self.download_dir)
                arcname = str(arcname).replace('\\', '/')  # replace backslashes with forward slashes
                if str(arcname) not in archive.namelist():
                    #print("image not in archive " + str(arcname))
                    #print(archive.namelist())
                    archive.write(image_path, arcname=arcname)

            if media_folder.exists():
                for filename in os.listdir(media_folder):
                    media_file_path = media_folder / filename
                    media_file_path_copy = images_path / filename
                    shutil.copyfile(media_file_path, media_file_path_copy)
                    arcname = media_file_path_copy.relative_to(self.download_dir)
                    arcname = str(arcname).replace('\\', '/')  # replace backslashes with forward slashes
                    print("if" + str(arcname) + " " + str(archive.namelist()))
                    if str(arcname) not in archive.namelist():
                        archive.write(media_file_path_copy, arcname=arcname)

    def _guess_extension_from_url(self, url: str) -> str:
        path = urlparse(url).path
        extension = Path(path).suffix
        if extension in self.supported_images_extensions:
            return extension
        return ""

    def _guess_extension_from_content_type(self, content_type: str) -> str:
        extension = mimetypes.guess_extension(content_type)
        if extension in self.supported_images_extensions:
            return extension
        return ""

    def _fill_image_metadata(
        self, image: dict, images_path: Path, extension: str
    ) -> Path:
        image_name = hashlib.md5(image["url"].encode()).hexdigest()
        image_filename = f"{self.slug}-{image_name}{extension}"
        image["name"] = image_filename
        image_path = images_path / image_filename
        return image_path

    def _download_image(
        self, image: dict, images_path: Path, force: bool
    ) -> Optional[Path]:
        extension_from_url = self._guess_extension_from_url(image["url"])
        image_path = self._fill_image_metadata(image, images_path, extension_from_url)

        # Do not redownload existing image (if known extension).
        # If the extension is unknown we have to retrieve it to guess
        # the mimetype from the content type and no cache is effective.
        if not force and image_path.exists():
            return image_path

        image_url = image["url"]
        if not image_url.startswith("http"):
            self.errors.append(f"`{image_url}` is not a valid image URL.")
            return None

        # We specify a custom user-agent (vs. default one `python-httpx/X.Y.Z`)
        # otherwise services like imgur will not return an image, see #33 for details.
        headers = {"user-agent": f"stylo-export/{httpx.__version__}"}
        timeout = httpx.Timeout(SE_IMAGES_TIMEOUT)
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(image_url, follow_redirects=True, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self.errors.append(e.args[0])
            return None

        if response.history:
            # There was a redirection so we compute all file path/name again,
            # but we keep the original url to be able to replace it
            # in the md file.
            image["original_url"] = image["url"]
            image["url"] = str(response.url)
            extension_from_url = self._guess_extension_from_url(image["url"])
            image_path = self._fill_image_metadata(
                image, images_path, extension_from_url
            )

        content_type = response.headers.get("content-type", "")
        extension_from_content_type = self._guess_extension_from_content_type(
            content_type
        )
        # We override the guessed extension from URL with the guessed
        # extension from the content-type (supposed to be more accurate).
        if (
            extension_from_content_type
            and extension_from_content_type != extension_from_url
        ):
            image_path = self._fill_image_metadata(
                image, images_path, extension_from_content_type
            )

        image_path.write_bytes(response.content)
        return image_path

    def fetch_all(
        self, templates_folder: Path, version: str = "", force: bool = False
    ) -> None:
        stylo_data = self.get_stylo_data(version)
        if stylo_data is not None:
            self.save_files(stylo_data)
        self.extract_metadata()
        self.extract_images()
        self.download_images(templates_folder, force=force)

    def export(
        self,
        version: str,
        formats: List["str"],
        style_name: str,
        templates_folder: Path,
        with_toc: bool = False,
        with_ascii: bool = False,
    ) -> Path:
        zip_file_path = self.download_dir / (
            f"{self.slug}-{self.id}-{version}-{'-'.join(sorted(formats))}-"
            f"toc-{int(with_toc)}-ascii-{int(with_ascii)}.zip"
        )
        # Ensure there is no on-disk cache for the generated zip file.
        zip_file_path.unlink(missing_ok=True)

        if version:
            # TODO: we probably don't need to refetch everything + call Stylo API again.
            self.fetch_all(templates_folder, version)

        try:
            self.generate_archive(
                zip_file_path,
                formats,
                style_name,
                templates_folder,
                with_toc,
                with_ascii,
            )
        except httpx.HTTPStatusError as exc:
            error = f"Erreur pendant la génération de « {self.title} »"
            if hasattr(exc, "url"):
                error += f" ({exc.url})"
            if hasattr(exc, "detail"):
                error += f" : {exc.detail}"
            self.errors.append(error)

        return zip_file_path

    def _write_to_archive(self, archive: ZipFile, file_name: Path) -> None:
        """A wrapper to generate correct relative paths within the archive."""
        arcname = file_name.relative_to(self.download_dir.parent)
        arcname = str(arcname).replace('\\', '/')  # replace backslashes with forward slashes
        if str(arcname) not in archive.namelist():
            archive.write(file_name, arcname=arcname)

    @property
    def bib_original_filepath(self) -> Path:
        bib_filepath: Path = self.download_dir / "originals" / self.filenames["bib"]
        return bib_filepath

    @property
    def bib_original_file_content(self) -> str:
        return self.bib_original_filepath.read_text()

    def generate_archive(
        self,
        zip_file_path: Path,
        formats: List["str"],
        style_name: str,
        templates_folder: Path,
        with_toc: bool,
        with_ascii: bool,
    ) -> None:
        images_config_path = self.edition_configuration.get("images_path", "images")
        csl_file_path = get_env_var("SE_STYLES_DIR") / f"{style_name}.csl"

        bib_file_path = self.download_dir / self.filenames["bib"]
        bib_file_path.write_text(self.bib_original_filepath.read_text())

        yaml_original_file_name = (
            self.download_dir / "originals" / self.filenames["yaml"]
        )
        yaml_file_path = self.download_dir / self.filenames["yaml"]
        yaml_content = yaml_original_file_name.read_text()
        if "bibliography:" in yaml_content:
            yaml_content = yaml_content.replace(
                f"{self.metadata.get('id_sp', self.id)}.bib", f"{self.slug}.bib"
            )
        else:
            yaml_dict = next(yaml.safe_load_all(yaml_content))
            yaml_dict["bibliography"] = f"{self.slug}.bib"
            yaml_content = yaml.safe_dump_all(
                [{}, yaml_dict, {}], default_flow_style=False
            )
            # We remove the added empty dicts necessary to retrieve the same structure
            # (one YAML document within a multiple one structure ---, dunno why).
            yaml_content = yaml_content[3:-3]
        yaml_file_path.write_text(yaml_content)

        md_original_file_name = self.download_dir / "originals" / self.filenames["md"]
        md_file_path = self.download_dir / self.filenames["md"]

        md_content = md_original_file_name.read_text()
        
        # TODO: Fix this
        # IL FAUT DÉCOMMENTER ÇA POUR QUE LES IMAGES SOIENT PRISES LOCALEMENT (ça ne fonctionne pas pour l'instant, je ne sais pas pourquoi)
        # for image in self.images:
        #     md_content = md_content.replace(
        #         # Useful in case of image URL redirection.
        #         image.get("original_url", image["url"]),
        #         f"{images_config_path}/{image['name']}",
        #     )

        # It happens with iframes from Youtube but the XML parser hates
        # these lazy HTML attributes.
        md_content = md_content.replace(
            "allowfullscreen>", 'allowfullscreen="allowfullscreen">'
        )
        md_content = md_content.replace(
            "œ", 'oe'
        )
        # We want to make sure there are non-breaking spaces before and after guillemets.
        md_content = md_content.replace(
            "« ", '«&nbsp;'
        )
        md_content = md_content.replace(
            " »", '&nbsp;»'
        )

        md_file_path.write_text(md_content)



        pandocapi = PandocAPI(md_file_path, yaml_file_path, bib_file_path)

        with ZipFile(zip_file_path, mode="a") as archive:
            # We want images for all kinds of exports.
            images_path = self.download_dir / images_config_path
            images_path.mkdir(parents=True, exist_ok=True)
            for image in self.images:
                image_file_path = images_path / image["name"]
                self._write_to_archive(archive, image_file_path)

            # In case of Sens-Public for instance, we want to add
            # media referenced in the template with article's images.
            media_folder = templates_folder / images_config_path
            if media_folder.exists():
                for filename in os.listdir(media_folder):
                    media_file_path = media_folder / filename
                    media_file_path_copy = images_path / filename
                    shutil.copyfile(media_file_path, media_file_path_copy)
                    self._write_to_archive(archive, media_file_path_copy)

            if "originals" in formats:
                self._write_to_archive(archive, bib_file_path)
                self._write_to_archive(archive, yaml_file_path)
                self._write_to_archive(archive, md_file_path)
            if "html" in formats:
                export_file_name = f"{self.slug}.html"
                export_file_path = self.download_dir / export_file_name
                template_file_path = templates_folder / "templateHtml5.html5"
                response = pandocapi.html(
                    export_file_name,
                    template_file_path,
                    csl_file_path,
                    with_toc,
                    with_ascii,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "tex" in formats:
                export_file_name = f"{self.slug}.tex"
                export_file_path = self.download_dir / export_file_name
                template_file_path = templates_folder / "templateLaTeX.latex"
                response = pandocapi.tex(
                    export_file_name,
                    template_file_path,
                    csl_file_path,
                    with_toc,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "xml-tei" in formats:
                export_file_name = f"{self.slug}-tei.xml"
                export_file_path = self.download_dir / export_file_name
                template_file_path = templates_folder / "template-tei.tei"
                response = pandocapi.xml_tei(
                    export_file_name,
                    template_file_path,
                    csl_file_path,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "xml-tei-metopes" in formats:
                export_file_name = f"{self.slug}-metopes-tei.xml"
                export_file_path = self.download_dir / export_file_name
                template_file_path = templates_folder / "template-tei.tei"
                xsl_file_path = templates_folder / "template-metopes.xsl"
                response = pandocapi.xml_tei_metopes(
                    export_file_name,
                    template_file_path,
                    csl_file_path,
                    xsl_file_path,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "xml-erudit" in formats:
                export_file_name = f"{self.slug}-erudit.xml"
                export_file_path = self.download_dir / export_file_name
                template_file_path = templates_folder / "template-xhtml.html"
                xsl_file_path = templates_folder / "template-erudit.xsl"
                response = pandocapi.xml_erudit(
                    export_file_name,
                    template_file_path,
                    csl_file_path,
                    xsl_file_path,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "pdf" in formats:
                export_file_name = f"{self.slug}.pdf"
                export_file_path = self.download_dir / export_file_name
                images_file_path = self.download_dir / "images.zip"
                template_file_path = templates_folder / "templateLaTeX.latex"
                print("calling pandoc API")
                response = pandocapi.pdf(
                    export_file_name,
                    images_file_path,
                    template_file_path,
                    csl_file_path,
                    with_toc,
                    style_name,
                )
                # print(archive)
                # print(response)
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "odt" in formats:
                export_file_name = f"{self.slug}.odt"
                export_file_path = self.download_dir / export_file_name
                images_file_path = self.download_dir / "images.zip"
                response = pandocapi.odt(
                    export_file_name,
                    images_file_path,
                    csl_file_path,
                    with_toc,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "docx" in formats:
                export_file_name = f"{self.slug}.docx"
                export_file_path = self.download_dir / export_file_name
                images_file_path = self.download_dir / "images.zip"
                response = pandocapi.docx(
                    export_file_name,
                    images_file_path,
                    csl_file_path,
                    with_toc,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
            if "icml" in formats:
                export_file_name = f"{self.slug}.icml"
                export_file_path = self.download_dir / export_file_name
                images_file_path = self.download_dir / "images.zip"
                response = pandocapi.icml(
                    export_file_name,
                    images_file_path,
                    csl_file_path,
                    style_name,
                )
                export_file_path.write_bytes(response.content)
                self._write_to_archive(archive, export_file_path)
