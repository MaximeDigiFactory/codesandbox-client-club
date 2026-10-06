#!/usr/bin/env python3
"""Restore exact fixed-release assets; no install scripts, no mutable refs."""
from pathlib import Path
import hashlib,requests,zipfile,io,shutil,json
p=Path(__file__).resolve().parents[1];lock=json.loads((p/'club/SOURCE-LOCK.json').read_text())
b=requests.get('https://github.com/LibreChat-AI/codesandbox-client/releases/download/bundler-v12/bundler.zip',timeout=180);b.raise_for_status();assert hashlib.sha256(b.content).hexdigest()==lock['archiveSHA256']
root=p/'state/runtime';root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(b.content)) as z:
 for name in z.namelist():assert not name.startswith('/') and '..' not in Path(name).parts
 z.extractall(root)
f=root/'static/js/sandbox.5f40c6a02.js';s=f.read_text();needle='fetch("https://col.csbops.io/data/sandpack",{method:"POST",body:JSON.stringify(n),headers:{Accept:"application/json","Content-Type":"application/json"}})';assert s.count(needle)==1;f.write_text(s.replace(needle,'Promise.resolve()'))
f=root/'index.html';f.write_text(f.read_text().replace('<head>','<head><script>window._env_={IS_ONPREM:"true"};</script>',1))
shutil.copytree(p/'club/static-browser-server-1.0.3/preview',p/'state/preview',dirs_exist_ok=True)
for name,digest in lock['staticAssetsSHA256'].items():assert hashlib.sha256((p/'state/preview'/name).read_bytes()).hexdigest()==digest
for name,m in lock.get('previewVendorAssets',{}).items():assert hashlib.sha256((p/'club/vendor'/name).read_bytes()).hexdigest()==m['SHA256']
print('Fixed archive verified; telemetry disabled; native static relay restored')
