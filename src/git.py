import subprocess
import os
from src.source import Source

class Git:
    def __init__(self,version,source:Source) -> None:
        self.version = version
        self.source = source
        self.is_init = False

    def init(self):
        os.chdir(self.source.make(self.version).parsed.as_posix())
        subprocess.run(['git','init','-q'])
        subprocess.run(['git', 'checkout', '-q', '-b', self.version], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'actions-user'])
        subprocess.run(['git', 'config', 'user.email', 'actions@github.com'])
        tags = subprocess.run(['git','remote'], capture_output=True).stdout.decode('utf-8').split('\n')
        add_or_not = 'origin' in tags
        subprocess.run(['git', 'remote', 'set-url' if add_or_not else 'add' ,'origin',f'https://x-access-token:{os.getenv("github-token")}@github.com/{os.getenv("github-repository")}'])
        subprocess.run(['git', 'fetch', '-q', '--tags', 'origin', self.version])
        self.is_init = True

    def commit(self):
        if(not self.is_init):
            return 'ERROR'
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-q', '-m', '🚀 boom burst the big bang'])
        subprocess.run(['git', 'tag', '-f', self.version])
        subprocess.run(['git', 'push','-f','-q', '--tags', 'origin'])
        os.chdir('..')