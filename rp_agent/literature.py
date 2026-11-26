"""Literature search and BibTeX retrieval from open scholarly APIs.

Sources: OpenAlex (broad, peer-reviewed + preprints), arXiv (recent preprints),
Semantic Scholar (optional; used when reachable, set S2_API_KEY for reliable access),
and doi.org / arxiv.org for authoritative BibTeX.
"""

from __future__ import annotations

import html
import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = "rp-agent/0.1 (research paper structuring tool)"
TIMEOUT = 25
STOPWORDS = {"a", "an", "the", "of", "for", "and", "or", "in", "on", "with", "to", "via", "using", "by", "based", "is"}


def _get(url: str, headers: dict | None = None) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", errors="replace")


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def _abstract_from_inverted(inv: dict | None) -> str:
    if not inv:
        return ""
    words = sorted((pos, w) for w, positions in inv.items() for pos in positions)
    return " ".join(w for _, w in words)


def search_openalex(query: str, limit: int, year_from: int | None) -> list[dict]:
    params = {
        "search": query,
        "per-page": str(limit),
        "select": "id,doi,title,publication_year,authorships,primary_location,cited_by_count,abstract_inverted_index,type",
    }
    if year_from:
        params["filter"] = f"from_publication_date:{year_from}-01-01"
    data = json.loads(_get("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))
    out = []
    for w in data.get("results", []):
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        out.append({
            "source": "openalex",
            "id": (w.get("id") or "").rsplit("/", 1)[-1],
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "title": w.get("title") or "",
            "year": w.get("publication_year"),
            "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])[:6] if a.get("author")],
            "venue": venue,
            "type": w.get("type"),
            "citations": w.get("cited_by_count"),
            "abstract": _abstract_from_inverted(w.get("abstract_inverted_index")),
        })
    return out


def search_arxiv(query: str, limit: int, year_from: int | None) -> list[dict]:
    terms = [t for t in re.findall(r"[A-Za-z0-9\-]+", query) if t.lower() not in STOPWORDS][:8]
    if not terms:
        return []
    q = " AND ".join(f"all:{t}" for t in terms)
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "max_results": str(limit), "sortBy": "relevance"})
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(_get(url))
    out = []
    for e in root.findall("a:entry", ns):
        year = int((e.findtext("a:published", "", ns) or "0000")[:4] or 0)
        if year_from and year < year_from:
            continue
        arxiv_id = (e.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        doi_el = e.find("arxiv:doi", ns)
        out.append({
            "source": "arxiv",
            "id": arxiv_id,
            "doi": doi_el.text if doi_el is not None else "",
            "title": " ".join((e.findtext("a:title", "", ns) or "").split()),
            "year": year,
            "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)][:6],
            "venue": "arXiv",
            "type": "preprint",
            "citations": None,
            "abstract": " ".join((e.findtext("a:summary", "", ns) or "").split()),
        })
    return out


def search_semantic_scholar(query: str, limit: int, year_from: int | None) -> list[dict]:
    params = {"query": query, "limit": str(limit),
              "fields": "title,year,authors,venue,citationCount,abstract,externalIds"}
    if year_from:
        params["year"] = f"{year_from}-"
    headers = {"x-api-key": os.environ["S2_API_KEY"]} if os.environ.get("S2_API_KEY") else None
    data = json.loads(_get("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params), headers))
    out = []
    for p in data.get("data", []):
        ext = p.get("externalIds") or {}
        out.append({
            "source": "semantic_scholar",
            "id": p.get("paperId"),
            "doi": ext.get("DOI", ""),
            "arxiv": ext.get("ArXiv", ""),
            "title": p.get("title") or "",
            "year": p.get("year"),
            "authors": [a.get("name") for a in (p.get("authors") or [])[:6]],
            "venue": p.get("venue") or "",
            "type": None,
            "citations": p.get("citationCount"),
            "abstract": p.get("abstract") or "",
        })
    return out


def search_literature(query: str, limit: int = 10, year_from: int | None = None,
                      sources: list[str] | None = None) -> dict:
    sources = sources or ["openalex", "arxiv", "semantic_scholar"]
    fns = {"openalex": search_openalex, "arxiv": search_arxiv, "semantic_scholar": search_semantic_scholar}
    results, notes, seen = [], [], set()
    for s in sources:
        if s not in fns:
            continue
        try:
            items = fns[s](query, limit, year_from)
        except (urllib.error.URLError, TimeoutError, ET.ParseError, json.JSONDecodeError, ValueError) as e:
            notes.append(f"{s}: unavailable ({e})")
            continue
        for it in items:
            key = (it.get("doi") or "").lower() or _norm_title(it["title"])
            if not key or key in seen:
                continue
            seen.add(key)
            if len(it.get("abstract", "")) > 900:
                it["abstract"] = it["abstract"][:900] + " ..."
            results.append(it)
    return {"query": query, "count": len(results), "results": results, "notes": notes}


# ---------------------------------------------------------------- BibTeX

def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def make_key(bibtex: str) -> str:
    author = re.search(r"\bauthor\s*=\s*[{\"]([^}\"]*)", bibtex, re.I)
    year = re.search(r"\byear\s*=\s*[{\"]?\s*(\d{4})", bibtex, re.I)
    title = re.search(r"\btitle\s*=\s*[{\"]+([^}\"]+)", bibtex, re.I)
    last = "anon"
    if author and author.group(1).strip():
        first = _ascii(author.group(1)).split(" and ")[0].strip()
        # "Wu, Qingqing" -> "Wu"; "Ashish Vaswani" -> "Vaswani"
        last = first.split(",")[0].strip() if "," in first else (first.split() or ["anon"])[-1]
    word = next((w for w in re.findall(r"[A-Za-z]+", _ascii(title.group(1))) if w.lower() not in STOPWORDS), "x") if title else "x"
    return re.sub(r"[^a-z0-9]", "", f"{last}{year.group(1) if year else ''}{word}".lower())


def _clean_bibtex(raw: str, key: str) -> str:
    raw = raw.strip().replace("–", "--").replace("—", "---")
    # Some publishers return HTML entities (e.g. "&amp;"); decode them and escape bare "&" for LaTeX.
    raw = re.sub(r"(?<!\\)&", r"\\&", html.unescape(raw))
    raw = re.sub(r"^@(\w+)\s*\{\s*[^,]*,", lambda m: f"@{m.group(1)}{{{key},", raw, count=1)
    # One field per line for readability.
    raw = re.sub(r",\s*(\w+)\s*=", r",\n  \1 = ", raw)
    raw = re.sub(r"\s*\}\s*$", "\n}", raw)
    return raw


def fetch_bibtex(identifier: str) -> str:
    """Return BibTeX for a DOI, arXiv ID or OpenAlex work ID (W...)."""
    ident = identifier.strip()
    ident = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", ident, flags=re.I)
    ident = re.sub(r"^(https?://arxiv\.org/abs/|arxiv:)", "", ident, flags=re.I)
    if re.match(r"^10\.\d{4,9}/\S+$", ident):
        bib = _get("https://doi.org/" + urllib.parse.quote(ident, safe="/:;()._-"),
                   {"Accept": "application/x-bibtex; charset=utf-8"})
        if not bib.lstrip().startswith("@"):
            raise ValueError(f"doi.org returned no BibTeX for {ident}")
        return bib
    if re.match(r"^(\d{4}\.\d{4,5}|[a-z\-]+(\.[A-Z]{2})?/\d{7})(v\d+)?$", ident):
        bib = _get(f"https://arxiv.org/bibtex/{ident}")
        if not bib.lstrip().startswith("@"):
            raise ValueError(f"arXiv returned no BibTeX for {ident}")
        return bib
    if re.match(r"^W\d+$", ident):
        w = json.loads(_get(f"https://api.openalex.org/works/{ident}"))
        if w.get("doi"):
            return fetch_bibtex(w["doi"])
        authors = " and ".join(a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author"))
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        return (f"@misc{{x,\n  title = {{{w.get('title','')}}},\n  author = {{{authors}}},\n"
                f"  year = {{{w.get('publication_year','')}}},\n  howpublished = {{{venue}}},\n"
                f"  note = {{OpenAlex {ident}}}\n}}")
    raise ValueError("Identifier must be a DOI (10.xxxx/...), an arXiv ID (e.g. 2101.01234) or an OpenAlex ID (W123...).")


def bibtex_entry(identifier: str, key: str | None = None) -> tuple[str, str]:
    raw = fetch_bibtex(identifier)
    key = key or make_key(raw)
    return key, _clean_bibtex(raw, key)


def bib_keys(bib_text: str) -> list[str]:
    return re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_text)
