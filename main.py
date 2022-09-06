from pathlib import Path
from src.source import Source
import importlib
import numpy as np
import threading

source = Source('./source')
reader = importlib.import_module('readers.v1', package=None).Reader(source)
items = list(Path().glob("./source/**/*.json"))
reader.read('1.19.2',False)
# for v in source.versions:
#     if(source.is_support(v)):
#         reader.read(v,False)