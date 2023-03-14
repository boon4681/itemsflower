import subprocess
import os
from src.source import Source
import random

class ActionGit:
    def __init__(self,version,source:Source) -> None:
        self.version = version
        self.source = source
        self.is_init = False

    def init(self):
        os.chdir(self.source.make(self.version).parsed.as_posix())
        subprocess.run(['git','init','-q'])
        subprocess.run(['git', 'checkout', '-q', '-b', 'data'], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'actions-user'])
        subprocess.run(['git', 'config', 'user.email', 'actions@github.com'])
        tags = subprocess.run(['git','remote'], capture_output=True).stdout.decode('utf-8').split('\n')
        add_or_not = 'origin' in tags
        subprocess.run(['git', 'remote', 'set-url' if add_or_not else 'add' ,'origin',f'https://x-access-token:{os.getenv("github-token")}@github.com/{os.getenv("github-repository")}'])
        subprocess.run(['git', 'fetch', '-q', '--tags', 'origin', 'data'])
        subprocess.run(['git', 'reset', '-q', '--hard', f'origin/data'])
        self.is_init = True

    def commit(self):
        if(not self.is_init):
            return 'ERROR'
        subprocess.run(['git', 'add', '.'])
        wow_a_commit = random.choice(['🌕 gouda go to get cheese', '🍵 a cup of tea','🍀 clover work well'])
        subprocess.run(['git', 'commit', '-q', '-m', wow_a_commit])
        subprocess.run(['git', 'push','-f', 'origin','data'])
        subprocess.run(['git', 'tag', '-f', self.version])
        subprocess.run(['git', 'push','-f', 'origin',self.version])
        os.chdir('..')

class UserGit:
    def __init__(self,version,source:Source) -> None:
        self.version = version
        self.source = source
        self.is_init = False

    def init(self):
        os.chdir(self.source.make(self.version).parsed.as_posix())
        subprocess.run(['git','init','-q'])
        subprocess.run(['git', 'checkout', '-q', '-b', 'data'], capture_output=True)
        tags = subprocess.run(['git','remote'], capture_output=True).stdout.decode('utf-8').split('\n')
        add_or_not = 'origin' in tags
        subprocess.run(['git', 'remote', 'set-url' if add_or_not else 'add' ,'origin', 'https://github.com/boon4681/itemsflower.git'])
        subprocess.run(['git', 'fetch', '-q', '--tags', 'origin', 'data'])
        subprocess.run(['git', 'reset', '-q', '--hard', f'origin/data'])
        self.is_init = True

    def commit(self):
        if(not self.is_init):
            return 'ERROR'
        subprocess.run(['git', 'add', '.'])
        wow_a_commit = random.choice(['🌕 gouda go to get cheese', '🍵 a cup of tea','🍀 clover work well'])
        subprocess.run(['git', 'commit', '-q', '-m', wow_a_commit])
        subprocess.run(['git', 'push','-f', 'origin','data'])
        subprocess.run(['git', 'tag', '-f', self.version])
        subprocess.run(['git', 'push','-f', 'origin',self.version])
        os.chdir('..')