import re, html as html_lib

import requests

from config import USER_AGENT, HOST, ITEMS_PER_PAGE, TIMEOUT


def read_category(file_path : str):
    with open(file_path, "r", encoding="utf-8") as file:
        return ["/" + line.strip("/") + "/" for line in file.read().split()]




def get_items_link(category):
    response = requests.get(HOST +  category,
                            params={
                                 "items_per_page": ITEMS_PER_PAGE,
                                "layout": "products_multicolumns", "result_ids": "pagination_contents", "is_ajax": 1,
                            },
                            headers=USER_AGENT,
                            timeout=TIMEOUT,
                            )

    html = response.json()["html"]["pagination_contents"]
    items_url = list(dict.fromkeys(re.findall(r'<a href="https://fragstore\.ua(/[^"]+/)"\s+class="product-title"', html)))
    return items_url

def get_brand_name(category):


    response = requests.get(HOST +  category,
                            params={
                                 "items_per_page": ITEMS_PER_PAGE,
                                "layout": "products_multicolumns", "result_ids": "pagination_contents", "is_ajax": 1,
                                "toggle_filter.set": "Y"
                            },
                            headers=USER_AGENT,
                            timeout=TIMEOUT,
                            )

    requests.post(HOST + "/index.php?dispatch=toggle_filter.set",
                                 data={
                                     "dispatch": "toggle_filter.set", "is_ajax": 1
                                 },
                                 headers=USER_AGENT,
                                 timeout=TIMEOUT,
                                 )
    html = response.json()["html"]['pagination_contents']
    brands = re.findall(r'data-brand="([^"]*)"', html)
    brands = [html_lib.unescape(b) for b in brands if b]
    return list(dict.fromkeys(brands))  # унікальні, порядок збережено


def get_filters(category):
    """Повертає id варіантів брендів (фільтр 64) і максимальну ціну (фільтр 176) для категорії."""
    response = requests.get(HOST + category, headers=USER_AGENT, timeout=TIMEOUT)
    html = response.text
    brand_ids = list(dict.fromkeys(re.findall(r'data-ca-filter-id="64" value="(\d+)"', html)))
    m = re.search(r'id="slider_\d+_176_right"[^>]*value="(\d+)"', html)
    max_price = int(m.group(1)) if m else 0
    return {"brands": brand_ids, "max_price": max_price}


def filtered_items_from_low_to_high_price(category):
    response = requests.get(HOST + category, headers=USER_AGENT, timeout=TIMEOUT,
                            params={
                                "sort_by": "price",
                                "sort_order": "asc",
                                "full_render": "true",
                                "result_ids": "fs_sorting,pagination_contents",
                                "is_ajax": 1
                            })
    html = response.json()["current_url"]
    return html