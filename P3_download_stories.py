import requests
import bs4
import pandas as pd
from dspipe import Pipe
import time
from pathlib import Path
from itertools import chain


"""
Downloads only the first page of each story, later stages of the pipeline
check and download additionally pages if needed.
"""


n_downloads = 2
fail_time = 120

sess = requests.session()


def proxy(url):
    # Comment the line below to use the proxy
    return sess.get(url)
    
    port = 8000
    host = "" # Fill this in with a proper host
    proxy_url = f"{host}:{port}"
    return requests.get(proxy_url, params={"url": url})


def collect(f_html):

    with open(f_html) as FIN:
        soup = bs4.BeautifulSoup(FIN.read(), "lxml")

    links = []
    for a in soup.find_all("a", href=True):
        link = a["href"]
        # 'www.literotica.com/i/' are image stories

        if "www.literotica.com/s/" not in link:
            continue

        link = link.split("/s/")[-1]

        links.append(link)

    # if not len(links):
    #    print(f"Note: {f_html} has no text links")

    return links


def download(f0, f1):
    print(f0, f1)

    url = "https://www.literotica.com/s/" + f0

    try:
        # r = sess.get(url)
        r = proxy(url)

    except:
        print(f"Failed to download {url}")
        time.sleep(fail_time)
        return False

    if not r.ok:
        print(f"Failed to download {url}")
        time.sleep(fail_time)
        return False

    html = r.content
    soup = bs4.BeautifulSoup(html, "lxml")

    # Remove the scripting and styling
    for name in ["script", "style"]:
        for block in soup.find_all(name):
            block.decompose()

    with open(f1, "w") as FOUT:
        FOUT.write(str(soup))

    time.sleep(1)


P = Pipe("data/story_listings/", input_suffix=".html", limit=None)
links = P(collect, -1)
links = list(chain(*links))


Pipe(links, "data/stories", output_suffix=".html", shuffle=True)(download, n_downloads)
