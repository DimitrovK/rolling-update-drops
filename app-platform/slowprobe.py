"""Start a 20 s request every second, each on its own connection; record what happens to each."""
import sys, time, threading, json, http.client, urllib.parse, ssl
URL, SECONDS, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
SLEEP = float(sys.argv[4]) if len(sys.argv) > 4 else 20
u = urllib.parse.urlparse(URL); ctx = ssl.create_default_context()
res, lock = [], threading.Lock()
def one():
    t0 = time.time()
    try:
        c = http.client.HTTPSConnection(u.hostname, 443, timeout=SLEEP + 90, context=ctx)
        c.request("GET", f"/slow?s={SLEEP}"); r = c.getresponse()
        out = dict(start=t0, end=time.time(), status=r.status, body=r.read().decode(errors="replace")[:80])
        c.close()
    except Exception as e:
        out = dict(start=t0, end=time.time(), status=0, body=f"{type(e).__name__}: {str(e)[:60]}")
    with lock: res.append(out)
ts = []; end = time.time() + SECONDS
while time.time() < end:
    t = threading.Thread(target=one, daemon=True); t.start(); ts.append(t); time.sleep(1.0)
for t in ts: t.join(timeout=SLEEP + 100)
json.dump(res, open(OUT, "w"))
ok = [r for r in res if r["status"] == 200]
print(f"slow requests={len(res)} ok={len(ok)} failed={len(res)-len(ok)}")
from collections import Counter
print("   failures:", dict(Counter(r["body"][:40] if r["status"]==0 else r["status"] for r in res if r["status"]!=200)))
