
import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class JobURLExtractor:

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
        )
    }

    @staticmethod
    def _validate_url(url: str):
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only HTTP and HTTPS URLs are supported.")

        if not parsed.hostname:
            raise ValueError("Invalid URL.")

        if parsed.username or parsed.password:
            raise ValueError("URLs containing credentials are not allowed.")

        try:
            addresses = socket.getaddrinfo(
                parsed.hostname,
                None,
                type=socket.SOCK_STREAM
            )

            for address in addresses:
                ip = ipaddress.ip_address(address[4][0])

                if not ip.is_global:
                    raise ValueError(
                        "Private or local URLs are not allowed."
                    )

        except socket.gaierror as error:
            raise ValueError("Unable to resolve the website hostname.") from error

    @classmethod
    def extract(cls, url: str) -> dict:

        url = url.strip()

        if not url:
            raise ValueError("Please provide a job posting URL.")

        current_url = url

        try:
            with requests.Session() as session:

                for _ in range(6):
                    cls._validate_url(current_url)

                    response = session.get(
                        current_url,
                        headers=cls.HEADERS,
                        timeout=20,
                        allow_redirects=False
                    )

                    if response.is_redirect:
                        location = response.headers.get("Location")

                        if not location:
                            raise ValueError("Invalid redirect.")

                        current_url = urljoin(current_url, location)
                        continue

                    response.raise_for_status()

                    content_type = response.headers.get(
                        "Content-Type", ""
                    ).lower()

                    if "text/html" not in content_type:
                        raise ValueError(
                            "The URL does not contain an HTML job page."
                        )

                    soup = BeautifulSoup(response.text, "html.parser")

                    for element in soup([
                        "script", "style", "nav", "footer",
                        "header", "aside", "noscript", "svg"
                    ]):
                        element.decompose()

                    title = (
                        soup.title.get_text(" ", strip=True)
                        if soup.title else "Job Posting"
                    )

                    main = (
                        soup.find("main")
                        or soup.find("article")
                        or soup.body
                        or soup
                    )

                    text = main.get_text(
                        separator="\n",
                        strip=True
                    )

                    text = "\n".join(
                        line.strip()
                        for line in text.splitlines()
                        if line.strip()
                    )

                    if len(text) < 100:
                        raise ValueError(
                            "Not enough readable text was found. "
                            "The website may require authentication "
                            "or block automated access. "
                            "Please paste the job description manually."
                        )

                    return {
                        "text": text,
                        "title": title,
                        "url": current_url,
                        "character_count": len(text),
                        "source": "URL"
                    }

                raise ValueError("Too many redirects.")

        except requests.RequestException as error:
            raise ValueError(
                f"Unable to retrieve the job posting: {error}"
            ) from error
