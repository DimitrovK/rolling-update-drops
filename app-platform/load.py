"""Continuous keep-alive HTTPS load; records every request's outcome and which version answered."""
import sys, time, threading, json, http.client, urllib.parse, ssl
URL, SECONDS, THREADS, OUT = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
u = urllib.parse.urlparse(URL); ctx = ssl.create_default_context()
res, lock, stop = [], threading.Lock(), threading.Event()
def worker():
    conn = None
    while not stop.is_set():
        t0 = time.time()
        try:
            if conn is None:
                conn = http.client.HTTPSConnection(u.hostname, 443, timeout=10, context=ctx)
            conn.request("GET", "/")
            r = conn.getresponse(); body = r.read().decode(errors="replace")[:60]
            out = (t0, time.time()-t0, r.status, body)
            if r.status >= 500 or r.getheader("connection","").lower() == "close":
                conn.close(); conn = None
        except Exception as e:
            out = (t0, time.time()-t0, 0, type(e).__name__ + ":" + str(e)[:40])
            try: conn.close()
            except Exception: pass
            conn = None
        with lock: res.append(out)
        time.sleep(0.05)
ts = [threading.Thread(target=worker, daemon=True) for _ in range(THREADS)]
for t in ts: t.start()
time.sleep(SECONDS); stop.set()
for t in ts: t.join(timeout=12)
json.dump(res, open(OUT, "w"))
ok = sum(1 for r in res if r[2] == 200); bad = [r for r in res if r[2] != 200]
print(f"requests={len(res)} ok={ok} failed={len(bad)}")
from collections import Counter
for k, v in Counter((r[2], r[3].split(":")[0] if r[2]==0 else r[3][:30]) for r in bad).most_common(8):
    print(f"   {v:>5}  status={k[0]} {k[1]}")
gens = Counter(r[3].split("gen=")[-1] for r in res if r[2]==200 and "gen=" in r[3])
print("   answered by:", dict(gens))
