"""Read-only checks for the deployed calculator."""
import argparse, json, time
from urllib.request import urlopen
from urllib.error import URLError
def verify(base):
    def read(path):
        with urlopen(base.rstrip('/')+path,timeout=20) as r: return r.read()
    if json.loads(read('/health')).get('status')!='healthy': raise RuntimeError('Health check failed')
    if not b'calorie' in read('/').lower(): raise RuntimeError('Calculator page did not render')
    read('/static/app.js'); read('/static/style.css'); print('PASS: health, calculator and assets')
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('url'); p.add_argument('--attempts',type=int,default=12); a=p.parse_args()
    for i in range(a.attempts):
        try: verify(a.url); break
        except (URLError,RuntimeError,ValueError,TimeoutError) as e:
            if i+1==a.attempts: raise SystemExit(f'Release verification failed: {e}')
            time.sleep(10)
