from __future__ import annotations
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, quote_plus
import re
import requests
from bs4 import BeautifulSoup
from ..config import settings

HEADERS = {"User-Agent": settings.user_agent, "Accept": "text/html,application/xhtml+xml"}

@dataclass
class ScrapedJob:
    source: str
    title: str
    company: str
    location: str
    closing_date: str
    posted_date: str
    url: str
    description: str
    category: str = ""


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def get_html(url: str) -> BeautifulSoup:
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()
    return BeautifulSoup(res.text, "lxml")


def scrape_graduates24(category: str = "internships", limit: int = 30) -> list[ScrapedJob]:
    paths = {
        "internships": "/internshipprogrammes",
        "graduate": "/graduate_programmes",
        "learnerships": "/learnerships",
        "entry": "/entry_level_jobs",
        "government": "/sa-government-internships-2026",
        "youth": "/youth_opportunities",
    }
    base = "https://www.graduates24.com"
    url = base + paths.get(category, "/internshipprogrammes")
    soup = get_html(url)
    jobs: list[ScrapedJob] = []

    # Graduates24 normally exposes job cards with headings and Read More links.
    for heading in soup.find_all(["h2", "h3", "h4"]):
        title = clean(heading.get_text(" "))
        if not title or len(title) < 8:
            continue
        parent = heading.find_parent()
        block = clean(parent.get_text(" ") if parent else heading.get_text(" "))
        link = heading.find("a") or (parent.find("a") if parent else None)
        href = urljoin(base, link.get("href")) if link and link.get("href") else url
        if href == url:
            # Try nearby read more anchor
            nxt = parent.find_next("a", string=re.compile("Read More", re.I)) if parent else None
            if nxt and nxt.get("href"):
                href = urljoin(base, nxt.get("href"))
        posted = ""
        closing = ""
        location = "South Africa"
        m = re.search(r"Posted:\s*([^C]+?)(?:Closes:|$)", block, flags=re.I)
        if m: posted = clean(m.group(1))
        c = re.search(r"Closes:\s*([^\|]+?)(?:Read More|Share|$)", block, flags=re.I)
        if c: closing = clean(c.group(1))
        loc_m = re.search(r"Posted:\s*\d{1,2}\s+\w+\s+\d{4}\s+([^C]+?)(?:Closes:|$)", block, re.I)
        if loc_m: location = clean(loc_m.group(1))
        jobs.append(ScrapedJob("Graduates24", title, title.split(":")[0] if ":" in title else "", location, closing, posted, href, block, category))
        if len(jobs) >= limit:
            break
    # fallback: all links containing opportunity-like text
    if len(jobs) < 5:
        for a in soup.select("a[href]"):
            title = clean(a.get_text(" "))
            if re.search(r"intern|graduate|learnership|programme|opportunit", title, re.I):
                jobs.append(ScrapedJob("Graduates24", title, title.split(":")[0], "South Africa", "", "", urljoin(base, a["href"]), title, category))
                if len(jobs) >= limit: break
    return jobs


def scrape_careers24(keyword: str = "internship", location: str = "south-africa", limit: int = 30) -> list[ScrapedJob]:
    base = "https://www.careers24.com"
    safe_kw = quote_plus(keyword.strip() or "internship").replace("+", "-")
    safe_loc = quote_plus(location.strip() or "south-africa").replace("+", "-")
    url = f"{base}/jobs/lc-{safe_loc}/kw-{safe_kw}/"
    soup = get_html(url)
    jobs: list[ScrapedJob] = []
    # Prefer advert links
    seen = set()
    for a in soup.select('a[href*="/jobs/adverts/"]') + soup.select('a[href*="/now-hiring/"][href*="/jobs/adverts/"]'):
        title = clean(a.get_text(" "))
        href = urljoin(base, a.get("href"))
        if not title or href in seen:
            continue
        seen.add(href)
        container = a.find_parent(["article", "li", "div"])
        block = clean(container.get_text(" ") if container else title)
        posted = ""
        days = ""
        p = re.search(r"Posted:\s*([^\n]+?)(?:\d+\s+Days left|$)", block, re.I)
        if p: posted = clean(p.group(1))
        d = re.search(r"(\d+\s+Days left)", block, re.I)
        if d: days = d.group(1)
        loc = "South Africa"
        if "Gauteng" in block: loc = "Gauteng"
        elif "Western Cape" in block: loc = "Western Cape"
        elif "Cape Town" in block: loc = "Cape Town"
        jobs.append(ScrapedJob("Careers24", title, "", loc, days, posted, href, block, keyword))
        if len(jobs) >= limit: break
    # fallback headings from search snippets
    if not jobs:
        for h in soup.find_all(["h2", "h3", "h4"]):
            title = clean(h.get_text(" "))
            if len(title) > 4 and not title.lower().startswith("about"):
                link = h.find("a") or h.find_parent("a")
                href = urljoin(base, link.get("href")) if link and link.get("href") else url
                jobs.append(ScrapedJob("Careers24", title, "", "South Africa", "", "", href, title, keyword))
                if len(jobs) >= limit: break
    return jobs


def fetch_all_live_jobs(keyword: str = "IT internship", limit: int = 60) -> list[dict]:
    jobs: list[ScrapedJob] = []
    errors = []
    for cat in ["internships", "graduate", "learnerships", "entry"]:
        try:
            jobs.extend(scrape_graduates24(cat, limit=15))
        except Exception as exc:
            errors.append(f"Graduates24 {cat}: {exc}")
    for kw in [keyword, "information technology internship", "data analyst intern", "business analyst intern", "cloud intern", "WIL"]:
        try:
            jobs.extend(scrape_careers24(kw, "south-africa", limit=10))
        except Exception as exc:
            errors.append(f"Careers24 {kw}: {exc}")
    unique = {}
    for j in jobs:
        if j.url not in unique and j.title:
            unique[j.url] = asdict(j)
    data = list(unique.values())[:limit]
    for d in data:
        d["scrape_errors"] = errors
    return data
