import requests
import bs4
import pandas as pd
from dspipe import Pipe
import time


categories = open("data/categories.txt").read().strip().split("\n")
sess = requests.session()

data = []


def compute(url):
    print(url)

    # Append this so we start the first page
    first_page_url = url + "/1-page"

    r = sess.get(first_page_url)

    if not r.ok:
        msg = f"Failed to download {url}"
        raise ValueError(msg)

    soup = bs4.BeautifulSoup(r.content, "lxml")
    button = soup.find("select")

    # If this fails assume we only have 3 pages
    try:
        options = [int(x["value"]) for x in button.find_all("option", value=True)]
    except AttributeError:
        options = [1, 2, 3]

    data.append(
        {"url": url, "last_page": max(options),}
    )

    print(data[-1])

    time.sleep(1)


Pipe(categories, limit=None, shuffle=True)(compute, 1)

df = pd.DataFrame(data).set_index("url")
df.to_csv("data/categories_with_pages.csv")
