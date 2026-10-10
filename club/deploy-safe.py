#!/usr/bin/env python3
import subprocess,sys
assert len(sys.argv)==1,'This command deploys only librechat-artefacts'
r=subprocess.run(['/srv/projects/deploy.sh','deploy','librechat-artefacts','prod'],capture_output=True,text=True,cwd='/srv/projects')
print('librechat-artefacts deployment exit',r.returncode)
raise SystemExit(r.returncode)
