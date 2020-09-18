import jsonlines
import json
from dspipe import Pipe

f_save = "data/Literotica.jsonl"


def compute(f0):
    with open(f0) as FIN:
        js = json.load(FIN)

    FOUT.write(js)


with jsonlines.open(f_save, "w") as FOUT:
    Pipe("data/full_text/")(compute, 1)
