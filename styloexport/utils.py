import json
import os
from pathlib import Path
from typing import Any, Iterator, List, Tuple, Union
from urllib.parse import urlparse

from dotenv import load_dotenv

from .config import *  # noqa

load_dotenv()


def get_domain_from_url(url: str) -> str:
    return urlparse(url).netloc


def get_bibliographic_styles_choices() -> List[Tuple[str, str]]:
    """Return Chicago modified (first) + Zotero pre-selected styles."""
    return [("chicagomodified", "Chicago (modified)")] + [
        (style["name"], style["title"])
        for style in (
            json.loads(
                (get_env_var("SE_STYLES_DIR") / "styles-custom.json").read_text()
            )
        )
    ]


def get_env_var(name: str, default: Any = None) -> Any:
    """Get the env var from a .env file, fallback on config.py."""
    env_var = os.getenv(name)
    if env_var is None:
        try:
            # This is quite ugly.
            env_var = globals()[name]
        except KeyError as e:  # pragma: no cover
            print(f"Env var `{name}` not found.")
            if default is not None:
                return default
            else:
                raise e
    return env_var


def each_folder_from(
    source_dir: Path, exclude: Union[str, None] = None
) -> Iterator[os.DirEntry]:
    """Walk across the `source_dir` and return the folder paths."""
    for direntry in os.scandir(source_dir):
        if direntry.is_dir():
            if exclude is not None and direntry.name in exclude:
                continue
            yield direntry
