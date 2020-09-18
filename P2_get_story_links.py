import requests
import bs4
import pandas as pd
from dspipe import Pipe
import time

sess = requests.session()


def page_iterator():
    df = pd.read_csv("data/categories_with_pages.csv")

    for url, n_pages in zip(df.url, df.last_page):
        for n in range(n_pages):
            yield (url, n)


def compute(item, f1):
    base_url, n = item
    category = base_url.split("/")[-1]
    url = f"{base_url}/{n}-page"

    f1 = f1.parent / f"{category}_{n:04d}.html"
    if f1.exists():
        return False

    r = sess.get(url)

    if not r.ok:
        msg = f"Failed to download {url}"
        raise ValueError(msg)

    with open(f1, "wb") as FOUT:
        FOUT.write(r.content)

    time.sleep(2)


Pipe(page_iterator(), "data/story_listings", limit=None, shuffle=True, autoname=False)(
    compute, 1
)
