import re, asyncio
from playwright.async_api import async_playwright

async def scrape_results(domain: str):
    url = (
        "https://www.facebook.com/ads/library/?"
        "active_status=all&ad_type=all&country=US&is_targeted_country=false&"
        f"media_type=all&q={domain}&search_type=keyword_unordered&"
        "start_date[min]=2024-11-12&start_date[max]"
    )

    print(f"🌐 Visiting {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=90000)
        await asyncio.sleep(8)  # Wait for full JS render like Colab

        html = await page.content()
        await browser.close()

    match = re.search(r"~\s*(\d+)\s*results", html)
    if match:
        return {"domain": domain, "results": int(match.group(1))}
    else:
        return {"domain": domain, "results": 0, "note": "No visible results or blocked"}
