# fetching-library-python

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A unified, asynchronous Python fetching library designed for web scraping and API consumption. It seamlessly bridges static HTTP requests, REST APIs, and JavaScript-rendered dynamic web pages with cookie/session persistence.

---

## Features

- **Asynchronous & Fast**: Powered by `httpx` and `asyncio` for non-blocking I/O.
- **Static & Dynamic Scraping**:
  - `fetch_static`: Lightweight static HTML fetching with automatic redirect following.
  - `fetch_dynamic`: Full headless Chromium browser execution via Playwright for dynamic SPAs and client-side rendered content.
- **REST API Ready**: Built-in JSON request handling with defaults for headers, query params, and request payloads.
- **File Downloads**: `download_file` streams files to disk, creates parent directories, and supports reusing an HTTP client.
- **Session & Context Persistence**:
  - GUI helper (`save_context_gui`) to interactively log into websites and save session storage/cookies.
  - Re-inject authenticated states into headless scraping jobs.
- **Unified Response Envelope**: Every fetch returns a normalized `FetchResult` containing success status, raw payload, and UTC timestamp.

---

## Installation

### 1. Install via pip

Install directly from GitHub (requires Git):

```bash
pip install git+https://github.com/sol239/fetching-library-python.git
```

Replace `USERNAME` with the repository owner's GitHub username.

Alternatively, clone the repository and install it in editable mode:

```bash
git clone https://github.com/your-username/fetching-library-python.git
cd fetching-library-python
pip install -e .
```

For development and running tests:

```bash
pip install -e ".[dev]"
```

### 2. Browser Requirements (For Dynamic Fetching)

Dynamic fetching relies on Chromium. You have two options:

- **Option A (Default - System Chromium)**:
  Ensure Chromium is installed on your system (default path: `/usr/bin/chromium`):
  ```bash
  sudo apt-get install chromium-browser # Debian/Ubuntu
  ```
  Or specify a custom path with the `BROWSER_PATH` environment variable:
  ```bash
  export BROWSER_PATH="/usr/bin/google-chrome"
  ```

- **Option B (Playwright Managed Chromium)**:
  ```bash
  playwright install chromium
  playwright install-deps
  ```

---

## Quickstart

### 1. Static Web Scraping

Fetch standard web pages quickly without the overhead of a headless browser:

```python
import asyncio
from core import FetchingHelper, FetchResult


async def main():
    result: FetchResult = await FetchingHelper.fetch_static("https://example.com")

    if result.is_success:
        print(f"Fetched {len(result.content)} bytes at {result.utc}")
        print(result.content[:200])
    else:
        print(f"Failed: {result.content}")


asyncio.run(main())
```

---

### 2. Calling REST APIs

Make GET, POST, PUT, or DELETE requests with JSON serialization and default API headers:

```python
import asyncio
import json
from core import FetchingHelper, FetchResult


async def main():
    result: FetchResult = await FetchingHelper.fetch_api(
        url="https://jsonplaceholder.typicode.com/posts",
        method="GET",
        params={"userId": 1},
    )

    if result.is_success:
        posts = json.loads(result.content)
        print(f"Retrieved {len(posts)} posts:")
        print(posts[0]["title"])


asyncio.run(main())
```

---

### 3. Dynamic Page Rendering (Playwright)

Scrape modern Single Page Applications (SPAs) that require JavaScript execution:

```python
import asyncio
from core import FetchingHelper, FetchResult


async def main():
    result: FetchResult = await FetchingHelper.fetch_dynamic(
        url="https://quotes.toscrape.com/js/",
        wait_for_state="networkidle",  # Options: "domcontentloaded", "load", "networkidle"
        wait_for_timer_ms=1000,        # Optional extra wait in ms
    )

    if result.is_success:
        print("Rendered HTML length:", len(result.content))


asyncio.run(main())
```

---

### 4. Interactive Login & Session Reuse

Bypass login walls, multi-factor authentication (MFA), or CAPTCHAs interactively, and reuse the authenticated session for scraping:

#### Step 1: Save Session Interactively (GUI)
```python
import asyncio
from pathlib import Path
from core import FetchingHelper

# Opens an interactive browser window. Log in manually, then press Enter in terminal.
asyncio.run(
    FetchingHelper.save_context_gui(
        url="https://example.com/login",
        context_file=Path("session.json"),
    )
)
```

#### Step 2: Use Saved Session in Headless Mode
```python
import asyncio
from pathlib import Path
from core import FetchingHelper, FetchResult


async def main():
    result: FetchResult = await FetchingHelper.fetch_dynamic(
        url="https://example.com/dashboard",
        context_file=Path("session.json"),
        wait_for_state="networkidle",
    )
    print(result.content)


asyncio.run(main())
```

---

### 5. Downloading Files

Stream a file to a destination given as a string or `Path`. Parent directories are created automatically, and an existing destination file is overwritten:

```python
import asyncio
from pathlib import Path
import httpx
from core import FetchingHelper


async def main():
    await FetchingHelper.download_file(
        url="https://example.com/file.pdf",
        path=Path("downloads/file.pdf"),
    )

    # Reuse a client for multiple downloads.
    async with httpx.AsyncClient(timeout=60) as client:
        await FetchingHelper.download_file(
            url="https://example.com/image.png",
            path="downloads/image.png",
            client=client,
        )


asyncio.run(main())
```

The method returns `None` on success and raises `httpx.HTTPError` for HTTP status or network errors. When no client is supplied, it creates a client with a 60-second timeout and closes it afterward. A supplied client stays open for reuse.

---

## Core Architecture

### `FetchResult`
A unified data structure returned across all fetch methods:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `is_success` | `bool` | `True` if HTTP status $< 400$ and no runtime exceptions occurred. |
| `content` | `str` | Response payload (HTML, JSON text, or error message). |
| `utc` | `datetime` | UTC timestamp created when the result object is initialized. |

### `FetchingHelper`
Static utility class exposing:

- `download_file(url, path, client=None)`
- `fetch_static(url, timeout=10)`
- `fetch_api(url, method="GET", headers=None, params=None, json_data=None, timeout=10)`
- `fetch_dynamic(url, context_file=None, browser=None, wait_for_state="", wait_for_timer_ms=0)`
- `save_context_gui(url, context_file=Path("context.json"))`

---

## Configuration

| Environment Variable | Default | Description |
| :--- | :--- | :--- |
| `BROWSER_PATH` | `/usr/bin/chromium` | Path to the Chromium binary used by Playwright. |

---

## Testing

Run the test suite using `pytest`:

```bash
pytest
```

To run a specific test:

```bash
pytest tests/test_fetch_static.py
pytest tests/test_fetch_api.py
```

---

## License

This project is licensed under the MIT License.
