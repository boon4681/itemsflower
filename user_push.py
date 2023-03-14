from pathlib import Path
import subprocess
from src.source import Source
from src.git import UserGit
import importlib

source = Source('./source')
reader = importlib.import_module('readers.v1', package=None).Reader(source)
versions = source.version_ids
for version in versions[::-1]:
    if(source.is_support(version)):
        print(version)
        git = UserGit(version,source)
        git.init()
        reader.read(version,False)
        git.commit()

    # if(i==5):
    #     break
# l = [
# '1.19.2',
# '1.19.2-rc2',
# '1.19.2-rc1',
# '1.19.1',
# '1.19.1-rc3',
# ]
# for i in l:
#     subprocess.run(['git','push','origin',f':refs/tags/{i}'])
# subprocess.run(['git','tag','-d',*l])