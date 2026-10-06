#!/usr/bin/env python3
import sys,json,subprocess,pathlib
sys.path.insert(0,'/srv/projects/librechat-codeapi/scripts')
from native_recipe_common import session,BASE
p=pathlib.Path('/srv/projects/librechat/state/20261006-artefacts');v=json.loads((p/'generation.json').read_text());e=next(e for e in v['events'] if e.get('final'));s,u=session();files=[x for x in e['responseMessage']['attachments'] if x['filename'] in ['bilan.xlsx','bilan.docx','bilan.pdf','bilan.html']];auth={'token':s.headers['Authorization'][7:],'user':s.get(BASE+'/api/user').json(),'conversationId':v['started']['conversationId'],'files':files}
public='--public' in sys.argv
auth['public']=public
relay=''
if not public:
 relay=json.loads(subprocess.check_output(['docker','inspect','club-artefacts-tls-recette']))[0]['NetworkSettings']['Networks']['bridge']['IPAddress'];assert relay
root=pathlib.Path(__file__).resolve().parents[2]
cmd=['docker','run','--rm','-i','--user','0:1002','--memory','2g','--cpus','2','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges:true','-v',str(root/'state/browser-tools')+':/browser:ro','-v',str(root/'club/recipes')+':/recipes:ro','-v',str(p)+':/evidence','mcr.microsoft.com/playwright@sha256:5b8f294aff9041b7191c34a4bab3ac270157a28774d4b0660e9743297b697e48','node','/recipes/browser-ui.cjs']
if not public:cmd[4:4]=['--dns',relay]
r=subprocess.run(cmd,input=json.dumps(auth),text=True,capture_output=True);print(r.stdout);print('Browser exit',r.returncode)
if r.returncode:print(r.stderr[-1000:])
raise SystemExit(r.returncode)
