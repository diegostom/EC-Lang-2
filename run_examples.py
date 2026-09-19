from pathlib import Path
import subprocess, sys
root=Path(__file__).parent
for p in sorted((root/'examples').glob('*.ec')):
    print('\n===',p.name,'===')
    r=subprocess.run([sys.executable,str(root/'main.py'),str(p)],capture_output=True,text=True)
    print(r.stdout,end='')
    if r.stderr: print(r.stderr,end='')
