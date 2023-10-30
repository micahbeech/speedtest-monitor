import os
import platform
import subprocess
from pathlib import Path


# https://stackoverflow.com/questions/2996887/how-to-replicate-tee-behavior-in-python-when-using-subprocess
def openFile(filepath: Path):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

def runInShell(command: str) -> str:
    return subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout
