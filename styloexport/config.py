from pathlib import Path

SECRET_KEY = "TODO"

SE_PANDOC_API_BASE_URL = "http://127.0.0.1:8000/v20221126_219/"
SE_PANDOC_API_TIMEOUT = None
SE_STYLO_API_TIMEOUT = None
SE_IMAGES_TIMEOUT = 60
SE_ALLOWED_INSTANCE_BASE_URLS = (
    "https://stylo.huma-num.fr https://stylo-dev.huma-num.fr"
)
SE_DOWNLOAD_DIR = (Path() / "downloads").resolve()
SE_STYLES_DIR = (Path() / "styles").resolve()
SE_STYLES_FIELDS = "generic-base"
SE_SUPPORTED_IMAGES_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif"]
SE_GRAPHQL_TOKEN = ""

# `name` values are visible for the user.
SE_EDITIONS = {
    "generique": {
        "name": "Générique",
        "exports": [
            ("originals", "fichiers originaux (md, yaml et bib)"),
            ("html", "conversion HTML"),
            ("tex", "conversion LaTeX"),
            ("pdf", "conversion PDF"),
            ("odt", "conversion ODT (OpenOffice)"),
            ("docx", "conversion DOCX (Word)"),
            ("icml", "conversion ICML (Impress)"),
            ("xml-tei", "conversion XML-TEI"),
            ("xml-erudit", "conversion XML Erudit"),
            ("xml-tei-metopes", "conversion XML-TEI Commons (Métopes)"),
        ],
    },
    "sens-public": {
        "name": "Sens public",
        "exports": {
            "all": {
                "name": "Tous les exports",
                "formats": [
                    "originals",
                    "html",
                    "tex",
                    "pdf",
                    "xml-tei",
                    "xml-erudit",
                ],
            }
        },
        "images_path": "media",
    },
    "lampadaire": {
        "name": "Lampadaire",
        "exports": {
            "all": {
                "name": "all",
                "formats": [
                    "pdf",
                    "html",
                    "tex",
                ],
            },
            "pdf": {
                "name": "pdf",
                "formats": [
                    "pdf",
                ],
            },
            "tex": {
                "name": "tex",
                "formats": [
                    "tex",
                ],
            }
        },
        "images_path": "media",
    },
}
