import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from mcp.server.fastmcp import FastMCP
import re
import cloudscraper

# ================= FETCH BASE URL =================
scraper = cloudscraper.create_scraper()
init_url = "https://93abf96f-app.google-life.workers.dev/category-search/Grand+Theft+Auto+IV/Games/1/" # Initial URL to trigger Cloudflare bypass
r = scraper.get(init_url)

# Extract real redirect from JS
match = re.search(r't\s*=\s*"(https?://[^"]+)"', r.text)
if match:
    full_url = match.group(1)
    # Strip off anything after /category-search
    BASE_URL = full_url.split("/category-search")[0]
    print("BASE_URL:", BASE_URL)
else:
    BASE_URL = None
    print("No redirect URL found!")

# ================= CONFIG =================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

# qBittorrent WebUI
QB_URL = "http://localhost:8080"  # WebUI URL
QB_USER = "admin"
QB_PASS = "adminadmin"

# Create MCP server
mcp = FastMCP(name="1337xSearch", host="0.0.0.0", port=8050, stateless_http=True)

# ================= HELPERS =================
def get_magnet(torrent_page_url: str) -> str:
    r = scraper.get(torrent_page_url, headers=HEADERS)
    if r.status_code != 200:
        return ""
    soup = BeautifulSoup(r.text, "html.parser")
    magnet_tag = soup.select_one("a[href^='magnet:?xt']")
    return magnet_tag["href"] if magnet_tag else ""

def search_1337x(query: str, page: int = 1, limit: int = 5, category: str = None):
    print(f"[1337x] Searching for: '{query}' | Category: {category} | Page: {page} | Limit: {limit}")
    encoded_query = quote_plus(query)
    if category:
        encoded_category = quote_plus(category)
        url = f"{BASE_URL}/category-search/{encoded_query}/{encoded_category}/{page}/"
    else:
        url = f"{BASE_URL}/search/{encoded_query}/{page}/"
    print("Search URL:", url)

    r = scraper.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"[1337x] ERROR: Failed to fetch {url} (status {r.status_code})")
        raise Exception(f"Failed to fetch {url} (status {r.status_code})")

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    rows = soup.select("table.table-list tbody tr")

    for row in rows[:limit]:
        name_tag = row.select_one("td.name a:nth-of-type(2)")
        if not name_tag:
            continue
        name = name_tag.text.strip()
        link = urljoin(BASE_URL, name_tag["href"])
        seeders = row.select_one("td.seeds").text.strip()
        leechers = row.select_one("td.leeches").text.strip()
        size = row.select("td.size")[0].text.split("B")[0].strip() + "B"
        magnet = get_magnet(link)

        results.append({
            "name": name,
            "link": link,
            "seeders": seeders,
            "leechers": leechers,
            "size": size,
            "magnet": magnet,
            "category": category if category else "All"
        })
        print(f"[1337x] Found: {name} | Seeders: {seeders} | Leechers: {leechers} | Size: {size} | Magnet: {magnet}")

    return results

# ================= MCP TOOLS =================
@mcp.tool()
def search_torrents(query: str, limit: int = 1, category: str = None):
    results = search_1337x(query=query, limit=limit, category=category)
    return json.dumps(results)

@mcp.tool()
def download_torrent(magnet: str):
    print(f"[Download] Attempting to download magnet: {magnet}")
    try:
        s = requests.Session()
        login_resp = s.post(f"{QB_URL}/api/v2/auth/login", data={"username": QB_USER, "password": QB_PASS})
        if login_resp.text != "Ok.":
            print(f"[Download] Login failed: {login_resp.text}")
            return json.dumps({"success": False, "error": "Failed to login to qBittorrent"})

        add_resp = s.post(f"{QB_URL}/api/v2/torrents/add", data={"urls": magnet})
        if add_resp.status_code != 200:
            print(f"[Download] Failed to add torrent: {add_resp.text}")
            return json.dumps({"success": False, "error": f"Failed to add torrent: {add_resp.text}"})

        print(f"[Download] Torrent added successfully")
        return json.dumps({"success": True, "message": "Torrent added successfully"})

    except Exception as e:
        print(f"[Download] Exception: {str(e)}")
        return json.dumps({"success": False, "error": str(e)})

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("Running 1337x MCP server on 0.0.0.0:8050")
    mcp.run(transport="sse")
