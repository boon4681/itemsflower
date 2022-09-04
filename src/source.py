import json
import math
import re
import requests
from alive_progress import alive_bar
from pathlib import Path
import os
import zipfile
import subprocess

class Node:
    def __init__(self, text):
        match = re.match(
            r'(?:(\d+:\d+:))?(.+) ([^()\s]+)(\(.*\))? -> (.+)',
            text
        )
        if(match):
            self.original_name = match.group(3)
            self.name = match.group(5)
            self.type = match.group(2)
            self.input = match.group(4)
    def __str__(self):
        return f'{self.original_name} -> {self.name}'

class VersionPath:
    def __init__(self,version,location:Path):
        location = location.joinpath(version)
        self.colormap = location.joinpath('colormap')
        self.clientJAR = location.joinpath(f'{version}.jar')
        self.mapping = location.joinpath(f'{version}-mapping.txt')
        self.java = location.joinpath('raw','java')
        self.classes = location.joinpath('raw','classes')
        self.parsed = location.joinpath('parsed')
        self.note = location.joinpath('note.txt')
    def make(self):
        self.colormap.mkdir(parents=True, exist_ok=True)
        self.java.mkdir(parents=True, exist_ok=True)
        self.classes.mkdir(parents=True, exist_ok=True)
        self.parsed.mkdir(parents=True, exist_ok=True)

class Source:
    def __init__(self,location:str) -> None:
        if location.startswith('.'):
            self.location = Path(location).resolve()
        else:
            self.location = Path(location)
        self.location.mkdir(parents=True, exist_ok=True)
        version_manifest = 'https://launchermeta.mojang.com/mc/game/version_manifest_v2.json'
        data = json.loads(requests.get(version_manifest).text)
        versions = data['versions']
        versions.sort(reverse=True, key=lambda v: v['releaseTime'])

        self.version_ids = [i['id'] for i in versions]
        with open('mcnotsupport', 'r') as f: self.notsupport = list(map(lambda x: x.replace('\n',''),f.readlines()))
        self.versions = {self.version_ids[v]: versions[v] for v in range(len(self.version_ids))}
    
    def make(self,version):
        v = VersionPath(version,self.location)
        v.make()
        return v

    def fetch(self,version:str, chunk_size=2048):
        location = self.make(version)
        if(version not in self.version_ids):
            return "ERROR VERSION NOT FOUND"
        if(version in self.notsupport):
            return "ERROR NOT SUPPORT VERSION"
        if(location.clientJAR.exists()):
            print(f"Found cached of client.jar from Minecraft-{version}")
            return
        print(f"Fetching Meta from Minecraft-{version}")
        data = json.loads(requests.get(self.versions[version]['url']).text)
        clientOBJ = data['downloads']['client']
        with open(location.clientJAR, 'wb') as f:
            r = requests.get(clientOBJ['url'], stream=True)
            length = int(r.headers.get('content-length'))
            r.raise_for_status()
            with alive_bar(math.ceil(length/chunk_size), title=f"Downloading client.jar", bar="filling") as bar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    bar()
                    if chunk:
                        f.write(chunk)
                        f.flush()

    def fetch_mapping(self,version: str,classes) -> str:
        location = self.make(version)
        if(version not in self.version_ids):
            return "ERROR VERSION NOT FOUND"
        if(version in self.notsupport):
            return "ERROR NOT SUPPORT VERSION"
        print(f"Fetching Meta from Minecraft-{version}")
        data = json.loads(requests.get(self.versions[version]['url']).text)
        clientOBJ = data['downloads']['client_mappings']
        mapping = requests.get(clientOBJ['url']).text
        with open(location.mapping,'w') as f:
            f.write(mapping)
        i = 0
        for line in mapping.split('\n'):
            for c in classes:
                match = re.match(f'{c} -> (\w+)', line)
                if(match):
                    i+=1
                    break
        if(i == len(classes)):
            print(f"Minecraft-{version} available for parsing")
        else:
            print(f"Minecraft-{version} not available for parsing")
        return mapping

    def get_classes(self,version, classes):
        location = self.make(version)
        mapping = ''
        if(version not in self.version_ids):
            return "ERROR VERSION NOT FOUND"
        if(version in self.notsupport):
            return "ERROR NOT SUPPORT VERSION"

        # load mapping
        if(location.mapping.exists()):
            with open(location.mapping,'r') as f:
                mapping = f.read().split('\n')
        else:
            mapping = self.fetch_mapping(version,classes).split('\n')

        classes_map = {}
        stack = []
        read_inside = False
        class_name = ''
        _mapping_ = ''

        for line in mapping:
            if(read_inside and line.startswith(' ')):
                stack.append(Node(re.match(r'\s+(.+)', line).group(1)))
            elif(read_inside):
                classes_map[class_name] = {
                    'name': _mapping_, 'stack': stack}
                stack = []
                read_inside = False
            for c in classes:
                match = re.match(f'{c} -> (\w+)', line)
                if(match):
                    class_name = c
                    _mapping_ = match.group(1)
                    read_inside = True
                    break
        return classes_map

    def decompile_classes(self,version,classes_info):
        location = self.make(version)
        decompiled = False
        if(location.note.exists()):
            with open(location.note,'r') as f: decompiled = f.read().find('decompiled') != -1
        with zipfile.ZipFile(location.clientJAR,'r') as jar:
            if(decompiled): return
            for k in classes_info:
                info = classes_info[k]
                name = info["name"]
                file = location.classes.joinpath(f'{name}.class')
                with open(file, 'wb') as f:
                    f.write(jar.read(f'{name}.class'))
                subprocess.run(['java','-jar','jd-cli.jar','-od',f'{location.java}',f'{file}'])
            with open(location.colormap.joinpath('grass.png'),'wb') as f:
                f.write(jar.read('assets/minecraft/textures/colormap/grass.png'))
            with open(location.colormap.joinpath('foliage.png'),'wb') as f:
                f.write(jar.read('assets/minecraft/textures/colormap/foliage.png'))
        with open(location.note,'a') as f: f.write('decompiled')

    def read_java(self,version,info):
        location = self.make(version)
        with open(location.java.joinpath(f'{info["name"]}.java'), 'r') as f:
            return f.read()