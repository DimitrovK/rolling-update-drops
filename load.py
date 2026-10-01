"""Continuous keep-alive load. Records every request outcome with a timestamp."""
import sys, time, threading, json, http.client, urllib.parse
URL, SECONDS, THREADS = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
OUT = sys.argv[4]
u = urllib.parse.urlparse(URL)
res, lock, stop = [], threading.Lock(), threading.Event()
def worker():
    conn = None
    while not stop.is_set():
        t0 = time.time()
        try:
            if conn is None:
                conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=5)
            conn.request("GET", u.path or "/")
            r = conn.getresponse(); body = r.read()
            out = (t0, time.time()-t0, r.status, body.decode()[:40])
            if r.status >= 500: conn.close(); conn = None
        except Exception as e:
            out = (t0, time.time()-t0, 0, type(e).__name__)
            try: conn.close()
            except Exception: pass
            conn = None
        with lock: res.append(out)
        time.sleep(0.02)
ts = [threading.Thread(target=worker, daemon=True) for _ in range(THREADS)]
for t in ts: t.start()
time.sleep(SECONDS); stop.set()
for t in ts: t.join(timeout=8)
json.dump(res, open(OUT,"w"))
ok = sum(1 for r in res if r[2]==200)
bad = [r for r in res if r[2]!=200]
print(f"requests={len(res)} ok={ok} failed={len(bad)}")
from collections import Counter
for k,v in Counter((r[2], r[3] if r[2]==0 else "") for r in bad).most_common():
    print(f"   {v:>5}  status={k[0]} {k[1]}")
