import random
import re
from locust import HttpUser, task, tag
from config import DATA_DIR, USER_AGENT, HOST
from perf.clients.pages import category
from perf.data.get_items_id import get_items
from perf.data.moduls import read_category, get_items_link, get_filters
from perf.validators.common import (
    check_category_page,
    check_html_page,
    check_json_response,
    check_no_notification_errors,
    check_page_number,
    check_response_count_items,
    check_status_code,
    check_url_contains,
)

PRODUCT_IDS = get_items()

class TestUser(HttpUser):
    host = HOST


    def on_start(self):
        self.client.headers = USER_AGENT
        r = self.client.get("/fanovyi-odyah/", name="Category (on_start)")
        m = re.search(r'name="security_hash"[^>]*value="([^"]+)"', r.text)
        self.security_hash = m.group(1) if m else ""



    @tag("Critical")
    @task
    def check_api(self):
        with self.client.get("/", name="Homepage", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
            elif "<html" not in response.text.lower():
                response.failure("Response is not an HTML page")



    @tag("Critical")
    @task
    def category_add_item(self):
        pid = random.choice(PRODUCT_IDS)
        with self.client.post("/index.php",
                              data={
                                  f"dispatch[checkout.add..{pid}]": "",
                                  f"product_data[{pid}][product_id]": pid,
                                  f"product_data[{pid}][amount]": 1,
                                  "result_ids": "cart_status*,wish_list*,checkout*,account_info*,abt__ut2_wishlist_count",
                                  "redirect_url": "index.php?dispatch=categories.view&category_id=3535",
                                  "full_render": "Y",
                                  "is_ajax": 1,
                                  "security_hash": self.security_hash,
                              },
                              name="Add Item",
                              catch_response=True) as response:

            check_status_code(response)
            data = check_json_response(response)
            check_no_notification_errors(response, data)





class TestFS(HttpUser):
    host = HOST

    CATEGORIES = read_category(DATA_DIR / "category.csv")
    ITEMS = {c: get_items_link(c) for c in CATEGORIES}
    FILTERS = {c: get_filters(c) for c in CATEGORIES}

    def on_start(self):
        self.client.headers = USER_AGENT
        r = self.client.get("/", name="HomePage (on_start)")
        m = re.search(r'name="security_hash"[^>]*value="([^"]+)"', r.text)
        self.security_hash = m.group(1) if m else ""


    @task
    @tag("Critical")
    def go_to_category(self):
        i = random.choice(self.CATEGORIES)
        with category(self.client, i) as response:
            check_html_page(response)
            check_category_page(response, i)

    @task
    @tag("Critical")
    def open_product_card(self):
        som_category = random.choice(self.CATEGORIES)
        item_url = random.choice(self.ITEMS[som_category])
        with self.client.get(HOST + item_url, name="Open Product card", catch_response=True) as response:
            check_html_page(response)

    @task
    @tag("Critical")
    def category_pagination_pages(self):
        som_category = random.choice(self.CATEGORIES)
        for page in range(1, 5):
            with self.client.get(HOST + som_category + f"page-{page}/",
                                 name="Category pagination pages",
                                 catch_response=True) as response:

                check_html_page(response)
                check_category_page(response, som_category)
                check_page_number(response, page)

    @task
    @tag("Critical")
    def filters_in_category(self):
        som_category = random.choice(self.CATEGORIES)
        filters = self.FILTERS[som_category]
        if not filters["brands"] or not filters["max_price"]:
            return

        brand_id = random.choice(filters["brands"])
        price_from = random.randint(0, filters["max_price"] // 2)
        price_to = random.randint(price_from + 1, filters["max_price"])
        features_hash = f"64-{brand_id}_176-{price_from}-{price_to}-UAH"

        with self.client.get(som_category,
                             params={
                                 "features_hash": features_hash,
                                 "full_render": "true",
                                 "result_ids": "products_newest_pagination_contents,fs_sorting,product_filters_*,"
                                               "products_search_*,category_products_*,product_features_*,"
                                               "breadcrumbs_*,selected_filters_*",
                                 "is_ajax": 1,
                             },
                             name="Filters in category",
                             catch_response=True) as response:

            if not check_status_code(response):
                return
            data = check_json_response(response)
            if not data:
                return
            if features_hash not in data.get("current_url", ""):
                response.failure(f"Filter not applied: {data.get('current_url')}")
            elif "products_count" not in data:
                response.failure("No products_count in response")

            check_response_count_items(response)

    @task
    @tag("Critical")
    def sorting_in_category(self):
        som_category = random.choice(self.CATEGORIES)

        with self.client.get(HOST + som_category, headers=USER_AGENT,
                            name="Sorting in low to high price",
                            catch_response=True,
                            params={
                                "sort_by": "price",
                                "sort_order": "asc",
                                "full_render": "true",
                                "result_ids": "fs_sorting,pagination_contents",
                                "is_ajax": 1
                            }) as response:

            check_status_code(response)
            check_url_contains(response, "sort_by=price&sort_order=asc")

    @task
    @tag("Critical")
    def search_by_query(self):
        query = random.choice(["spider-man", "batman", "iron man"])
        with self.client.get(HOST,
                             name="Search by query",
                            headers=USER_AGENT, catch_response=True,
                             params={
                                    "match": "all",
                                    "subcats": "Y",
                                    "pcode_from_q": "Y",
                                    "pshort": "Y",
                                    "pfull": "Y",
                                    "pname": "Y",
                                    "pkeywords": "Y",
                                    "sl": "uk",
                                    "search_performed": "Y",
                                    "q": query,
                                    "dispatch": "products.search",
                                }) as response:

            check_status_code(response)


if __name__ == "__main__":

  from locust import run_single_user
  run_single_user(TestFS)