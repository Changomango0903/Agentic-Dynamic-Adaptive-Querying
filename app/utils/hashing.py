from urllib.parse import urlsplit, urlunsplit

def norm_url(u: str) -> str:
    if not u:
        return ""
    p = urlsplit(u)
    # drop fragments and query for dedupe purposes
    return urlunsplit((p.scheme, p.netloc.lower(), p.path, "", ""))