import sys


def assertPythonVersionAtLeast(version: tuple):
    if sys.version_info < version:
        sys.exit(1)
    
if __name__ == '__main__':
    version = tuple(map(int, sys.argv[1].split('.')))
    assertPythonVersionAtLeast(version)
