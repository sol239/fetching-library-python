import asyncio
import os
from pathlib import Path
from typing import Any

import httpx
from playwright.async_api import Browser, async_playwright

from .FetchResult import FetchResult

CONTEXT_FILE = Path("context.json")
BROWSER_PATH = os.environ.get("BROWSER_PATH", "/usr/bin/chromium")


class FetchingHelper:
    @staticmethod
    async def fetch_static(url: str, timeout: int = 10) -> FetchResult:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=timeout)

            # Check for 4xx and 5xx errors
            if response.status_code >= 400:
                return FetchResult(
                    is_success=False,
                    content=f"Request failed with status code {response.status_code}",
                )

            # Success: return response body text
            return FetchResult(
                is_success=True,
                content=response.text,
            )

        except httpx.HTTPError as e:
            # Handles DNS failures, timeouts, connection drops, etc.
            return FetchResult(
                is_success=False,
                content=f"Network error: {e}"
            )

    @staticmethod
    async def save_context_gui(url: str, context_file: Path = CONTEXT_FILE) -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                executable_path=BROWSER_PATH,
            )

            # Go to the url
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)

            await asyncio.to_thread(
                input,
                "The browser will close after pressing Enter...",
            )

            await context.storage_state(path=context_file)
            await browser.close()

    @staticmethod
    async def fetch_dynamic(
        url: str,
        context_file: Path | None = None,
        browser: Browser | None = None,
        wait_for_state: str = "",
        wait_for_timer_ms: int = 0,
    ) -> FetchResult:

        playwright = None
        browser_was_passed = browser is not None
        context = None

        try:
            if not browser_was_passed:
                playwright = await async_playwright().start()

                browser = await playwright.chromium.launch(
                    headless=True,
                    executable_path=BROWSER_PATH,
                )

            context = await browser.new_context(
                storage_state=context_file if context_file else None
            )

            page = await context.new_page()

            await page.goto(url)

            # Wait strategy
            if wait_for_timer_ms > 0:
                await page.wait_for_timeout(wait_for_timer_ms)

            if wait_for_state in {
                "domcontentloaded",
                "load",
                "networkidle",
            }:
                await page.wait_for_load_state(wait_for_state)

            html = await page.content()

            return FetchResult(
                is_success=True,
                content=html,
            )

        except Exception as e:
            return FetchResult(
                is_success=False,
                content=str(e),
            )

        finally:
            if context is not None:
                await context.close()

            # Close browser only if this method created it
            if not browser_was_passed and browser is not None:
                await browser.close()

            if playwright is not None:
                await playwright.stop()

    @staticmethod
    async def fetch_api(
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | list[Any] | None = None,
        timeout: int = 10,
    ) -> FetchResult:
        # Default REST headers
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "ApiClient/1.0",
        }
        if headers:
            default_headers.update(headers)

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=default_headers,
                    params=params,
                    json=json_data,  # Automatically sets 'Content-Type' and encodes the payload
                    timeout=timeout,
                )

            if response.status_code >= 400:
                return FetchResult(
                    is_success=False,
                    content=f"Request failed with status code {response.status_code}: {response.text}",
                )

            return FetchResult(
                is_success=True,
                content=response.text,
            )

        except httpx.HTTPError as e:
            return FetchResult(
                is_success=False,
                content=f"Network error: {e}",
            )
