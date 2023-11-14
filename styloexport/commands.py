import json
from pathlib import Path

import click
import httpx
from flask import Blueprint

from .utils import each_folder_from, get_env_var

blueprint = Blueprint("styles", __name__)


@blueprint.cli.command("download")  # type: ignore
@click.argument("url", default="https://www.zotero.org/styles-files/styles.json")
def download(
    url: str = "https://www.zotero.org/styles-files/styles.json",
    force_download: bool = False,
) -> None:  # pragma: no cover
    """Download JSON styles file from Zotero."""
    print(f"Downloading JSON styles file from Zotero: {url}")
    styles_dir = get_env_var("SE_STYLES_DIR")
    styles_dir.mkdir(parents=True, exist_ok=True)
    target = styles_dir / "styles-zotero.json"
    if target.exists() and not force_download:
        print(f"Styles from cache {styles_dir / 'styles-zotero.json'}")
        return

    try:
        response = httpx.get(url)
        response.raise_for_status()
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(
            (
                f"Error response {exc.response.status_code} "
                f"while requesting {exc.request.url!r}."
            )
        )

    content = response.text
    (styles_dir / "styles-zotero.json").write_text(content)
    print(f"Styles downloaded to {styles_dir / 'styles-zotero.json'}")


@blueprint.cli.command("reduce")  # type: ignore
def reduce() -> None:  # pragma: no cover
    """Download JSON styles file from Zotero."""
    print("Reducing JSON styles file from Zotero…")
    styles_dir = get_env_var("SE_STYLES_DIR")
    styles_fields = get_env_var("SE_STYLES_FIELDS")
    zotero_styles_text = (styles_dir / "styles-zotero.json").read_text()
    zotero_styles_json = json.loads(zotero_styles_text)
    custom_styles_json = []
    for zotero_style in zotero_styles_json:
        if zotero_style["dependent"] == 1:
            continue
        for field in styles_fields.split(","):
            if field in zotero_style["categories"]["fields"]:
                custom_styles_json.append(zotero_style)
    (styles_dir / "styles-custom.json").write_text(
        json.dumps(custom_styles_json, indent=2)
    )
    print(
        (
            f"…JSON reduced from {len(zotero_styles_json)} "
            f"to {len(custom_styles_json)} styles, "
            f"kept fields: {styles_fields.split(',')}"
        )
    )


@blueprint.cli.command("retrieve")  # type: ignore
def retrieve(force_download: bool = False) -> None:  # pragma: no cover
    """Retrieve CSL styles files from Zotero."""
    print("Retrieving CSL styles files from Zotero…")
    styles_dir = get_env_var("SE_STYLES_DIR")
    styles_text = (styles_dir / "styles-custom.json").read_text()
    styles_json = json.loads(styles_text)
    counter = 0
    for style in styles_json:
        name = style["name"]
        target = styles_dir / f"{name}.csl"
        if target.exists() and not force_download:
            continue
        url = style["href"]
        try:
            response = httpx.get(url)
            response.raise_for_status()
            counter += 1
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        except httpx.HTTPStatusError as exc:
            print(
                (
                    f"Error response {exc.response.status_code} "
                    f"while requesting {exc.request.url!r}."
                )
            )

        target.write_text(response.text)
    print(f"…{counter} CSL files retrieved from Zotero.org")


@blueprint.cli.command("custom")  # type: ignore
def custom() -> None:  # pragma: no cover
    """Deal with custom templates styles."""
    print("Copying styles from custom templates…")
    count = 0
    templates_folder = Path() / "templates"
    styles_folder = get_env_var("SE_STYLES_DIR")
    for folder in each_folder_from(templates_folder, exclude="templates"):
        for csl_file_path in Path(folder).glob("*.csl"):
            print(f"Copying {csl_file_path.name} from {csl_file_path}")
            (styles_folder / csl_file_path.name).write_text(csl_file_path.read_text())
            count += 1
    print(f"…{count} styles copied")
