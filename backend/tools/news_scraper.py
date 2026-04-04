# /backend/tools/news_scraper.py
import json
import asyncio
import random
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

async def scrape_yahoo_finance_news(ticker: str, max_retries: int = 3) -> str:
    url = f"https://finance.yahoo.com/quote/{ticker}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for attempt in range(max_retries):
            # Create a fresh context for every retry to clear potential blocks
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                timezone_id="America/New_York",
                geolocation={"longitude": -74.0060, "latitude": 40.7128},
                permissions=["geolocation"]
            )

            # THE FIX: Use the new class-based API and apply stealth to the entire context
            await Stealth().apply_stealth_async(context)

            page = await context.new_page()

            try:
                response = await page.goto(url, wait_until="networkidle", timeout=25000)

                # Check for 403 or other failures immediately
                if response and response.status == 403:
                    raise Exception("403 Forbidden detected")

                # Handle potential cookie walls
                try:
                    consent_btn = page.locator("button[name='agree'], .con-wizard button, button:has-text('Accept all')")
                    if await consent_btn.count() > 0:
                        await consent_btn.first.click(timeout=3000)
                except PlaywrightTimeoutError:
                    pass

                await page.wait_for_selector('h3', state='attached', timeout=10000)

                extraction_js = """
                () => {
                    const items = Array.from(document.querySelectorAll('section[data-test="qsp-news"] li, div[data-test="mrt-node-quoteNewsStream"] li, div[data-testid="news-stream"] li'));
                    const nodes = items.length > 0 ? items : Array.from(document.querySelectorAll('section div.content h3')).map(h => h.closest('div, li')).filter(Boolean);

                    const extracted = [];
                    const seenHeadlines = new Set();

                    for (const node of nodes) {
                        if (extracted.length >= 5) break;

                        const headlineEl = node.querySelector('h3');
                        const summaryEl = node.querySelector('p');

                        if (headlineEl && headlineEl.innerText.trim() !== '') {
                            let rawHeadline = headlineEl.innerText.trim();
                            rawHeadline = rawHeadline.replace(/^(Bloomberg|Reuters|Yahoo Finance|Motley Fool)\\s*-\\s*/i, '').trim();

                            if (seenHeadlines.has(rawHeadline)) continue;
                            seenHeadlines.add(rawHeadline);

                            const article = { headline: rawHeadline };

                            if (summaryEl) {
                                const summaryText = summaryEl.innerText.trim();
                                if (summaryText && summaryText.length > 10) {
                                    article.summary = summaryText;
                                }
                            }
                            extracted.push(article);
                        }
                    }
                    return extracted;
                }
                """
                articles = await page.evaluate(extraction_js)

                if articles:
                    await browser.close()
                    return json.dumps(articles, indent=2)

                raise Exception("No articles extracted (DOM might have changed)")

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {str(e)}")
                await context.close() # Close context before retrying

                if attempt < max_retries - 1:
                    # Exponential backoff: 2, 4, 8 seconds + random jitter
                    sleep_time = (2 ** (attempt + 1)) + random.uniform(0, 1)
                    await asyncio.sleep(sleep_time)
                else:
                    await browser.close()
                    return json.dumps([{"error": f"Failed after {max_retries} attempts: {str(e)}"}])

    return json.dumps([{"error": "Unexpected failure"}])
