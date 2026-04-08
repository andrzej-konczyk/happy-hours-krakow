import requests
import json
import re
import fitz  # pymupdf
from bs4 import BeautifulSoup
from datetime import datetime


KEYWORDS = [
    "happy hour", "happyhour",
    "promo", "promocja", "promocyjn",
    "2+1", "drugi gratis", "trzeci gratis",
    "discount", "zniżka", "znizka",
    "-30%", "-50%", "-20%",
    "tańsze", "taniej", "gratis",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

HTML_URLS = [
    "https://alchemia.com.pl/",
]

PDF_URLS = [
    "https://ckbrowar.pl/wp-content/uploads/2026/02/menu-web-01.2026.pdf",
]


# ── Fetching ──────────────────────────────────────────────────────────────────

def fetch_html_text(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def fetch_pdf_text(url: str) -> str | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        doc = fitz.open(stream=response.content, filetype="pdf")
        return " ".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"[ERROR PDF] {url}: {e}")
        return None


# ── Parsing ───────────────────────────────────────────────────────────────────

def find_snippets(text: str, window: int = 100) -> list[dict]:
    snippets = []
    text_lower = text.lower()

    for keyword in KEYWORDS:
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        for match in pattern.finditer(text_lower):
            idx = match.start()
            start = max(0, idx - window)
            end = min(len(text), idx + len(keyword) + window)
            snippet = text[start:end].strip()
            snippets.append({"keyword": keyword, "snippet": snippet})

    return snippets


# ── Scraping ──────────────────────────────────────────────────────────────────

def scrape_html(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        print(f"[HTML] {url}")
        text = fetch_html_text(url)
        if not text:
            results.append({"url": url, "type": "html", "status": "error", "snippets": []})
            continue
        snippets = find_snippets(text)
        print(f"       {len(snippets)} snippet(s) found")
        results.append({
            "url": url,
            "type": "html",
            "status": "ok",
            "scraped_at": datetime.now().isoformat(),
            "snippets": snippets,
        })
    return results


def scrape_pdfs(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        print(f"[PDF]  {url}")
        text = fetch_pdf_text(url)
        if not text:
            results.append({"url": url, "type": "pdf", "status": "error", "snippets": []})
            continue
        snippets = find_snippets(text)
        print(f"       {len(snippets)} snippet(s) found")
        results.append({
            "url": url,
            "type": "pdf",
            "status": "ok",
            "scraped_at": datetime.now().isoformat(),
            "snippets": snippets,
        })
    return results


# ── Output ────────────────────────────────────────────────────────────────────

def save_results(results: list[dict], output_path: str = "scraper/output.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Saved {len(results)} result(s) to {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = scrape_html(HTML_URLS) + scrape_pdfs(PDF_URLS)
    save_results(results)