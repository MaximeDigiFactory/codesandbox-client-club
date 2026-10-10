#!/usr/bin/env python3
"""Public TLS gate, then native-only configuration; deployment output suppressed."""
from pathlib import Path
import requests,yaml,subprocess,uuid,json,sys,hashlib
base='https://artefacts.digiconseil.fr';random='https://'+uuid.uuid4().hex+'-preview.artefacts.digiconseil.fr'
try:
 r=requests.get(base+'/version.txt',timeout=20);r.raise_for_status();assert r.text.strip()=='PROD-1741371360-5877b84','Unexpected bundler build'
 r=requests.get(random+'/__csb_relay/',headers={'Origin':'https://librechat.digiconseil.fr'},timeout=20);r.raise_for_status();assert 'Relay frame' in r.text;assert r.headers.get('Access-Control-Allow-Origin')=='https://librechat.digiconseil.fr';assert 'Content-Security-Policy' in r.headers;assert 'Set-Cookie' not in r.headers
 lock=json.loads((Path(__file__).parent/'SOURCE-LOCK.json').read_text())
 for name,digest in lock['runtimePatchedAssetsSHA256'].items():
  asset=requests.get(base+'/'+name,timeout=20);asset.raise_for_status();assert hashlib.sha256(asset.content).hexdigest()==digest, 'Unexpected runtime assets'
 for name,digest in lock['staticAssetsSHA256'].items():
  asset=requests.get(random+'/'+name,timeout=20);asset.raise_for_status();assert hashlib.sha256(asset.content).hexdigest()==digest, 'Unexpected static relay assets'
 for name,meta in lock['previewVendorAssets'].items():
  asset=requests.get(random+'/__csb_vendor/'+name,timeout=20);asset.raise_for_status();assert hashlib.sha256(asset.content).hexdigest()==meta['SHA256'], 'Unexpected native preview dependency'
except (requests.RequestException, AssertionError) as e:
 print("Preview activation refused: public HTTPS/wildcard gate not ready; no configuration changed.",flush=True)
 sys.exit(2)
print('Public TLS, wildcard, CORS, CSP and cookie gate passed',flush=True)
for project,service in [('librechat/preprod','librechat-preprod'),('librechat','librechat')]:
 p=Path('/srv/projects')/service;path=p/'docker-compose.yml';backup=p/'state/20261006-artefacts/docker-compose.before-preview.yml'
 if not backup.exists():backup.write_bytes(path.read_bytes())
 c=yaml.safe_load(path.read_text());env=c['services'][service]['environment'];names=['SANDPACK_BUNDLER_URL','SANDPACK_STATIC_BUNDLER_URL']
 assert isinstance(env,list)
 env[:]=[x for x in env if x.split('=',1)[0] not in names]
 env+=['SANDPACK_BUNDLER_URL=https://artefacts.digiconseil.fr','SANDPACK_STATIC_BUNDLER_URL=https://preview.artefacts.digiconseil.fr']
 path.write_text(yaml.safe_dump(c,sort_keys=False))
 r=subprocess.run(['/srv/projects/deploy.sh','deploy',project,'prod','--service='+service,'--no-deps'],capture_output=True,text=True)
 print(service,'deployment exit',r.returncode,flush=True)
 if r.returncode:
  path.write_bytes(backup.read_bytes());raise RuntimeError('Targeted deploy failed; compose restored, details suppressed')
print('Native preview variables activated on both instances; browser recipe required',flush=True)
