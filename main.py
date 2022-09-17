from pathlib import Path
from src.source import Source
from src.git import Git
import importlib
import numpy as np
import threading
import click

@click.command()
@click.option('--version',default='latest')
@click.option('--fetch/--no-fetch',default=True,type=bool)
def main(version:str,fetch:bool):
    source = Source('./source')
    git = Git(version,source)
    if version == 'latest': version = source.version_ids[0]
    reader = importlib.import_module('readers.v1', package=None).Reader(source)
    reader.read(version,fetch)
    git.init()
    git.commit()
# for v in source.versions:
#     if(source.is_support(v)):
#         reader.read(v,False)

if __name__ == '__main__':
    main()