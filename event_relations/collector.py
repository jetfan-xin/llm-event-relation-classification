"""Bounded ConceptNet collection with pagination and retained attribution fields."""

import json
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
from .evaluation import RELATIONS


def collect(max_pages=1, fetch=None):
    if type(max_pages) is not int or not 1 <= max_pages <= 100:
        raise ValueError("max_pages must be an integer between 1 and 100 per relation")
    if fetch is None:
        def fetch(url):
            with urlopen(url, timeout=20) as response:
                return json.load(response)
    result = {rel: [] for rel in RELATIONS}
    for rel in RELATIONS:
        url = f"https://api.conceptnet.io/query?rel=/r/{rel}&limit=1000"
        visited, seen = set(), set()
        for _ in range(max_pages):
            if url in visited:
                break
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "api.conceptnet.io":
                raise ValueError("Unexpected pagination host or protocol")
            visited.add(url)
            page = fetch(url)
            for edge in page["edges"]:
                if edge.get("rel", {}).get("@id") != "/r/" + rel:
                    continue
                if any(edge.get(side, {}).get("language") != "en" for side in ("start", "end")):
                    continue
                identity = edge.get("@id") or (edge["start"]["@id"], edge["end"]["@id"])
                if identity in seen:
                    continue
                seen.add(identity)
                result[rel].append(dict(start=edge["start"], end=edge["end"], text=edge.get("surfaceText"),
                                        edge_id=edge.get("@id"), license=edge.get("license"),
                                        sources=edge.get("sources", []), dataset=edge.get("dataset")))
            next_page = page.get("view", {}).get("nextPage")
            if not next_page:
                break
            url = urljoin("https://api.conceptnet.io", next_page)
            if url.startswith("http://api.conceptnet.io/"):
                url = "https://" + url[len("http://"):]
    return result
