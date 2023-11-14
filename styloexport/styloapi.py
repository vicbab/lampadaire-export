import httpx

from .utils import get_env_var

SE_STYLO_API_TIMEOUT = get_env_var("SE_STYLO_API_TIMEOUT")
SE_GRAPHQL_TOKEN = get_env_var("SE_GRAPHQL_TOKEN")


def call_styloapi(url: str, params: dict) -> httpx.Response:
    timeout = httpx.Timeout(SE_STYLO_API_TIMEOUT)
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {SE_GRAPHQL_TOKEN}",
    }

    with httpx.Client(base_url=url, timeout=timeout) as client:
        try:
            response = client.post("/graphql", headers=headers, json=params)
            response.raise_for_status()
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            exc.url = url  # type: ignore[attr-defined]
            raise exc
        except httpx.HTTPStatusError as exc:
            exc.url = url  # type: ignore[attr-defined]
            print(
                (
                    f"Error response {exc.response.status_code} "
                    f"while requesting {exc.request.url!r}."
                )
            )
            raise exc
    return response


class StyloAPI:
    def __init__(self, url: str) -> None:
        self.url = url

    def article(self, article_id: str) -> httpx.Response:
        parameters = {
            "query": """
                query($article:ID!) {
                    article(article:$article) {
                        _id
                        title
                        workingVersion {
                            md
                            bib
                            yaml (options: { strip_markdown: true })
                        }
                        versions {
                            _id
                            version
                            revision
                            message
                            md
                            bib
                            yaml (options: { strip_markdown: true })
                        }
                    }
                }
            """,
            "variables": {"article": article_id},
        }
        return call_styloapi(self.url, parameters)
