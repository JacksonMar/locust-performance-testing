import re

import requests

from config import USER_AGENT


def get_items():
    response = requests.get("https://fragstore.ua/index.php",
                            params={
                                  "dispatch": "products.search", "search_performed": "Y", "q": "", "sl": "uk",
                                  "sort_by": "timestamp", "sort_order": "desc", "items_per_page": 80,
                                  "layout": "products_multicolumns", "result_ids": "pagination_contents", "is_ajax": 1,
                            },
                            headers=USER_AGENT
                            )

    html = response.json()["html"]["pagination_contents"]
    ids = list(dict.fromkeys(re.findall(r'name="product_data\[(\d+)\]\[product_id\]"', html)))
    return ids