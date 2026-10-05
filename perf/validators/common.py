PRODUCT_MARKER = 'class="product-title"'


def check_html_page(response):
    if response.status_code != 200:
        response.failure(f"Expected 200, got {response.status_code}")
    elif "<html" not in response.text.lower():
        response.failure("Response is not an HTML page")


def check_category_page(response, category):
    if category not in response.url:
        response.failure("Response is not a expected category")


def check_status_code(response, expected=200):
    if response.status_code != expected:
        response.failure(f"Expected {expected}, got {response.status_code}")
        return False
    else:
        return True


def check_json_response(response):
    try:
        return response.json()
    except ValueError:
        response.failure("Response is not a valid JSON")
        return None


def check_no_notification_errors(response, data):
    notifications = data.get("notifications") or {}
    errors = [n["message"] for n in notifications.values() if n.get("type") == "E"]
    if errors:
        response.failure(f"Server error: {errors}")
        return False
    return True


def check_page_number(response, page):
    if page <= 1:
        return True
    if f"page-{page}" not in response.url:
        response.failure(f"Expected page {page} in URL, got {response.url}")
        return False
    return True


def check_response_count_items(response):
    try:
        data = response.json()
    except ValueError:
        response.failure("Response is not a valid JSON")
        return False
    return data.get("products_count", 0) > 0


def check_url_contains(response, expected_substring):
    if expected_substring in response.url:
        response.success()
    else:
        response.failure(f"Expected URL to contain '{expected_substring}', got {response.url}")

def check_has_products(response):
    if PRODUCT_MARKER not in response.text:
        response.failure("No products in the response")
        return False
    return True