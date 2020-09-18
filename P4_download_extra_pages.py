import requests
import bs4
import json
import pandas as pd
from dspipe import Pipe
import time
from pathlib import Path
from itertools import chain

"""
Downloads additional pages if needed for each story. Collects the text
for each story into a single file along with the meta information from
the first page.
"""

n_downloads = 4
fail_time = 120
sess = requests.session()


def proxy(url):
    # Comment the line below to use the proxy
    return sess.get(url)
    
    port = 8000
    host = "" # Fill this in with a proper host
    proxy_url = f"{host}:{port}"
    return requests.get(proxy_url, params={"url": url})


def download(f0, f1):

    with open(f0) as FIN:
        raw = FIN.read()

    soup = bs4.BeautifulSoup(raw, "lxml")

    page_text = soup.find("div", class_="b-pager-pages").span.text

    title = soup.find("div", class_="b-story-header").h1.get_text()
    author = soup.find("div", class_="b-story-header").a.get_text()

    stats = soup.find("span", class_="b-story-stats").text.split()
    cat = soup.find("div", class_="b-breadcrumbs").children

    meta = {
        "title": title,
        "author": author,
        "category": list(cat)[1].text,
        "n_comments": int(stats[0]),
        "n_views": int(stats[2]),
        "n_favorites": int(stats[4]),
        "n_pages": int(page_text.split()[0]),
    }

    next_btn = soup.find("a", text="Next")
    story = soup.find("div", class_="b-story-body-x").get_text()

    print(meta)

    while next_btn is not None:
        link = next_btn["href"]

        r = proxy(link)

        if not r.ok:
            print(f"Failed to download {url}")
            time.sleep(fail_time)
            return False

        soup = bs4.BeautifulSoup(r.content, "lxml")

        page_text = soup.find("div", class_="b-story-body-x")
        next_btn = soup.find("a", text="Next")

        # print(page_text)

        if page_text:
            story += page_text.get_text()

    item = {
        "text": story,
        "meta": meta,
    }

    js = json.dumps(item, indent=2)

    with open(f1, "w") as FOUT:
        FOUT.write(js)

    time.sleep(1)


def safe(f0, f1):
    try:
        download(f0, f1)
    except Exception as EX:
        print(f"FAILED {f0}, {EX}")


Pipe(
    "data/stories/",
    "data/full_text",
    input_suffix=".html",
    output_suffix=".json",
    shuffle=True,
    limit=None,
)(safe, n_downloads)
