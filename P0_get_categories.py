import requests
import pathlib
import bs4

dest = pathlib.Path("data")
dest.mkdir(exist_ok=True)

f_save = dest / "categories.txt"

url = "https://www.literotica.com/stories/"
r = requests.get(url)

if not r.ok:
    msg = f"Failed to download {url}"
    raise ValueError(msg)

html = r.content
soup = bs4.BeautifulSoup(html, "lxml")

with open(f_save, "w") as FOUT:
    for a in soup.find_all("a", href=True):
        link = a["href"]

        if "www.literotica.com/c/" not in link:
            continue

        print(link)

        FOUT.write(link + "\n")
