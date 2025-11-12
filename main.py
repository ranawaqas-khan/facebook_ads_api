import re, nest_asyncio, asyncio, random
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from playwright.async_api import async_playwright

nest_asyncio.apply()
app = FastAPI(title="Facebook Ads Library Scraper API")

PROXIES = [
    # "http://user:pass@proxy1:port",
    # "http://user:pass@proxy2:port",
]

class DomainRequest(BaseModel):
    domain: str

class BatchRequest(BaseModel):
    domains: List[str]

async def scrape_results(domain: str):
    url = (
        "https://www.facebook.com/ads/library/?"
        "active_status=all&ad_type=all&country=US&is_targeted_country=false&"
        f"media_type=all&q={domain}&search_type=keyword_unordered&"
        "start_date[min]=2024-11-12&start_date[max]"
    )

    proxy = random.choice(PROXIES) if PROXIES else None
    print(f"🌐 Visiting {url} {'via proxy ' + proxy if proxy else '(direct)'}")

    async with async_playwright() as p:
        launch_args = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
            ],
        }
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = await p.chromium.launch(**launch_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        page = await context.new_page()

        await page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["image", "font", "media"]
            else route.continue_(),
        )

        try:
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await asyncio.sleep(6)
            html = await page.content()
        except Exception as e:
            await browser.close()
            return {"domain": domain, "error": str(e)}

        await browser.close()

    match = re.search(r"~\s*(\d+)\s*results", html)
    if match:
        return {"domain": domain, "results": int(match.group(1))}
    else:
        return {"domain": domain, "results": 0, "note": "No visible results or blocked"}

@app.get("/check_ads")
async def check_ads(domain: str = Query(..., description="Domain to check (e.g., freedomsolarpower.com)")):
    try:
        return await scrape_results(domain)
    except Exception as e:
        return {"domain": domain, "error": str(e)}

@app.post("/check_ads")
async def check_ads_post(req: DomainRequest):
    try:
        return await scrape_results(req.domain)
    except Exception as e:
        return {"domain": req.domain, "error": str(e)}

@app.post("/batch_check")
async def batch_check(req: BatchRequest):
    results = []
    for domain in req.domains:
        try:
            result = await scrape_results(domain)
            results.append(result)
        except Exception as e:
            results.append({"domain": domain, "error": str(e)})
    return {"total": len(results), "data": results}

@app.get("/")
def root():
    return {
        "message": "✅ Facebook Ads Library Scraper API is running",
        "endpoints": ["/check_ads", "/batch_check"],
    }
