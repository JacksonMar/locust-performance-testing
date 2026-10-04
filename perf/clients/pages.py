
# - homepage(client): client.get("/", name="Homepage", catch_response=True)
# - category(client, url): запит з category_fanovyi_odyah

def homepage(client):
    return client.get("/", name="Homepage", catch_response=True)


def category(client, url):
    return client.get(url, name="Category", catch_response=True)