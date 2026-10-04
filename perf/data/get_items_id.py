import re

import requests

from config import USER_AGENT, HOST, ITEMS_PER_PAGE, TIMEOUT


def get_items():
    response = requests.get(HOST + "/index.php",
                            params={
                                  "dispatch": "products.search", "search_performed": "Y", "q": "", "sl": "uk",
                                  "sort_by": "timestamp", "sort_order": "desc", "items_per_page": ITEMS_PER_PAGE,
                                  "layout": "products_multicolumns", "result_ids": "pagination_contents", "is_ajax": 1,
                            },
                            headers=USER_AGENT,
                            timeout=TIMEOUT,
                            )

    html = response.json()["html"]["pagination_contents"]
    ids = list(dict.fromkeys(re.findall(r'name="product_data\[(\d+)\]\[product_id\]"', html)))
    return ids
