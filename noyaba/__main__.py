import sys
from .vm import VM
from .runtime import CenterError
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: python -m noyaba file.ny')
    try:
        path=sys.argv[1]
        VM(project_root=__import__('os').path.dirname(__import__('os').path.abspath(path))).run(open(path,encoding='utf8').read(),path)
    except CenterError as e: raise SystemExit(f'{type(e).__name__}: {e}')
