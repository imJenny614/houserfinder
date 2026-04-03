"""
Shared Playwright browser instance for all scrapers.
Call `get_browser()` to get a reusable browser, `close_browser()` on app shutdown.
"""
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext

_playwright = None
_browser: Optional[Browser] = None
_lock = asyncio.Lock()


async def get_browser() -> Browser:
    global _playwright, _browser
    async with _lock:
        if _browser is None or not _browser.is_connected():
            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
    return _browser


async def new_context(browser: Browser) -> BrowserContext:
    """Create a stealth browser context."""
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="en-SG",
        timezone_id="Asia/Singapore",
        extra_http_headers={"Accept-Language": "en-SG,en;q=0.9"},
    )
    # Hide webdriver fingerprint
    await ctx.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        window.chrome = { runtime: {} };
    """)
    return ctx


async def close_browser():
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
