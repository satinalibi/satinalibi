import json, base64, io, html, sys
from PIL import Image
sys.path.insert(0,'.')
import build
build.INCLUDE_ALL=True
posts=build.load_posts()
STYLE={'cover':'Magazine cover','moodboard':'Mood board','still':'Film still','edit':'Shop the edit','frames':'Film frames','contact':'Contact sheet','sun':'Red sun','flash':'Flash photo','darkroom':'Darkroom print','specimen':'Specimen card','fourways':'Four ways','museum':'Museum wall','lot':'Auction lot','howto':'How-to'}
order=['golden-hour','lace-and-pearls','after-dark','take-up-space']
# usage: python tools/review_page.py OUT.html [--pending] [--batch "Second batch"]
# --pending: only pins with no decision yet in content/pin-schedule.yml
args=sys.argv[1:]
only_pending='--pending' in args
batch=args[args.index('--batch')+1] if '--batch' in args else 'First batch'
import yaml, os
decided=set((yaml.safe_load(open('content/pin-schedule.yml')) or {}).keys()) if os.path.exists('content/pin-schedule.yml') else set()
pins=[]
for p in sorted(posts,key=lambda p:(order.index(p['section']),p['slug'])):
    for pin in p['pins']:
        if only_pending and pin['id'] in decided: continue
        pins.append((p,pin))
def thumb(pid):
    im=Image.open(f'scratch/live/pins/{pid}.jpg').convert('RGB').resize((560,840),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'JPEG',quality=74,optimize=True,progressive=True)
    return base64.b64encode(b.getvalue()).decode()
cards=[]
for p,pin in pins:
    t=html.escape(pin.get('pin_title') or p['title'])
    d=html.escape(pin.get('pin_description') or '')
    ptitle=html.escape(build.re.sub(r'\*','',p['title']))
    cards.append(f'''<article class="pin" data-id="{pin['id']}" data-board="{p['section']}">
<div class="shot"><img src="data:image/jpeg;base64,{thumb(pin['id'])}" alt="Pin: {t}" width="560" height="840" loading="lazy"><span class="badge" aria-hidden="true"></span></div>
<div class="meta"><span class="board b-{p['section']}">{html.escape(p['section_info']['name'])}</span><span class="kind">{STYLE.get(pin.get('style'),'Pin')}</span></div>
<h3>{t}</h3>
<p class="to">Links to <a href="{p['abs_url']}" target="_blank" rel="noopener">{ptitle}</a></p>
<details><summary>Pin description</summary><p>{d}</p></details>
<div class="act" role="group" aria-label="Decision for this pin"><button type="button" class="yes" data-act="approved" aria-pressed="false">Approve</button><button type="button" class="no" data-act="skipped" aria-pressed="false">Skip</button></div>
</article>''')
tpl=open('tools/review_template.html').read()
out=tpl.replace('%%CARDS%%','\n'.join(cards)).replace('%%COUNT%%',str(len(pins))).replace('%%BATCH%%',html.escape(batch))
path=args[0]
open(path,'w').write(out)
print(len(pins),'pins',round(len(out)/1e6,2),'MB')
