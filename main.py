from src.source import Source
import importlib

source = Source('./source')
reader = importlib.import_module('readers.v1', package=None).Reader(source)
for v in source.version_ids:
    if(v not in source.notsupport):
        reader.read(v)