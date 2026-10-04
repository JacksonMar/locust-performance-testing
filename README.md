# Locust Performance Testing — e-commerce storefront

Load and performance tests for a CS-Cart based online store ([fragstore.ua](https://fragstore.ua)), written in Python with [Locust](https://locust.io/).

The tests model a typical shopper journey: browsing categories, paginating, filtering, sorting, searching, opening product cards and adding items to the cart. Every request is validated (status code, HTML/JSON body, expected URL/content), so functional regressions under load are reported as failures, not just slow responses.

## Scenarios

| User class | Task | What is checked |
|---|---|---|
| `TestFS` | Open category | 200, HTML page, correct category URL |
| `TestFS` | Open product card | 200, HTML page |
| `TestFS` | Category pagination (pages 1–4) | 200, HTML, correct category and page number |
| `TestFS` | Filter by brand + price range (AJAX) | valid JSON, filter applied in `current_url`, `products_count` present |
| `TestFS` | Sort by price, low → high (AJAX) | 200, sort params in URL |
| `TestFS` | Search by query | 200 |
| `TestUser` | Homepage | 200, HTML page |
| `TestUser` | Add item to cart (AJAX, with `security_hash`) | 200, valid JSON, no error notifications |

All tasks are tagged `Critical`, so you can run subsets with `--tags` / `--exclude-tags`.

### Dynamic test data

Test data is not hardcoded: when a test starts, it scrapes the live site:

- category list from `perf/data/category.csv`
- product URLs for each category
- available brand filter IDs and the max price for each category
- product IDs for the add-to-cart scenario
- CSRF `security_hash` for each virtual user, taken in `on_start`

## Project structure

```
.
├── locustfile.py            # entry point: user classes and tasks
├── config.py                # host, headers, timeouts (env-overridable)
├── pyproject.toml           # dependencies + default Locust settings
└── perf/
    ├── clients/pages.py     # reusable page requests
    ├── data/                # test data: CSV + scrapers for product IDs, links, filters
    └── validators/common.py # response assertions (status, HTML, JSON, URL)
```

## Installation

Requires Python 3.14+.

```bash
git clone https://github.com/JacksonMar/locust-performance-testing.git
cd locust-performance-testing
```

**Option A: uv (recommended)**

```bash
# install uv once (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv

# create .venv and install dependencies from uv.lock
uv sync
```

**Option B: pip + venv**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install locust requests
```

## Running

With uv, prefix commands with `uv run`. With pip, activate `.venv` first and run them as-is.

```bash
# web UI at http://localhost:8089 (press Start in the browser)
uv run locust

# headless run with defaults from pyproject.toml (host, users, run-time, tags)
uv run locust --headless

# custom load: 5 users, spawn rate 1/s, run for 2 minutes
uv run locust --headless -u 5 -r 1 -t 2m

# run only one user class
uv run locust TestFS

# run only tasks with a given tag
uv run locust --tags Critical

# save HTML report and CSV stats
uv run locust --headless -t 2m --html report.html --csv results/stats

# single user, for debugging (one user, no load)
uv run python locustfile.py

# another target host
HOST=https://staging.example.com uv run locust --host https://staging.example.com
```

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `HOST` | `https://fragstore.ua` | target host |
| `ITEMS_PER_PAGE` | `80` | page size used when collecting test data |

## Results

Run on 2026-10-04: **5 concurrent users, 4 min 10 s**, all scenarios.

**681 requests · 0 failures · ~2.7 RPS · median 1.5 s · p95 3.9 s**

![Response time over the run: median ~1.5 s, p95 3–4 s](docs/response-times.svg)

| Request | Method | Requests | Failures | Median, ms | p95, ms | Max, ms |
|---|---|---:|---:|---:|---:|---:|
| Homepage | GET | 84 | 0 | 3,700 | 4,300 | 4,354 |
| Add Item | POST | 85 | 0 | 2,000 | 2,700 | 2,866 |
| Open Product card | GET | 55 | 0 | 1,600 | 5,500 | 7,788 |
| Search by query | GET | 54 | 0 | 1,600 | 1,800 | 2,007 |
| Category pagination pages | GET | 214 | 0 | 1,500 | 1,800 | 2,034 |
| Category | GET | 63 | 0 | 1,400 | 1,700 | 1,851 |
| Sorting in low to high price | GET | 63 | 0 | 1,300 | 1,600 | 1,964 |
| Filters in category | GET | 58 | 0 | 920 | 1,500 | 1,589 |
| **Aggregated** | | **681** | **0** | **1,500** | **3,900** | **7,788** |

*`on_start` requests (5 in total) are left out of the rows but counted in Aggregated.*

**Observations**

- **Homepage is the slowest page** (median 3.7 s). The response is ~1 MB of HTML, about twice the size of a category page. Good candidate for caching or lazy loading.
- **The product card has a long tail:** median 1.6 s, but p95 5.5 s and max 7.8 s. The slowness depends on the product, so a few heavy product pages are worth profiling.
- **AJAX endpoints are the fastest** (filters 0.9 s, sorting 1.3 s), because they return HTML fragments, not full pages.
- **No errors and stable latency** over the whole run. At this load the site shows no signs of degradation.

## Note on load

This is a learning/portfolio project that runs against a public production site. Tests were run only with low load (up to 5 concurrent users, ~3 RPS) for a few minutes, to avoid any impact on the store. Do not run high-concurrency tests against a site you do not own or have permission to test.
