from pathlib import Path
from src.source import Source
import importlib
import numpy as np
import threading

source = Source('./source')
reader = importlib.import_module('readers.v1', package=None).Reader(source)

def migrate(__range__):
    for v in __range__:
        if(source.is_support(v)):
            print(v)
            reader.read(v,False)

procs = []
for i in np.array_split(source.version_ids,5):
    p = threading.Thread(target=migrate,args=(i,))
    procs.append(p)
    p.start()

for proc in procs:
    proc.join()