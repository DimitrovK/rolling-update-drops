import json, re, pathlib, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"figure.facecolor":"#12141a","axes.facecolor":"#12141a","axes.edgecolor":"#3a4050",
 "text.color":"#e6e8ee","axes.labelcolor":"#e6e8ee","xtick.color":"#9aa3b5","ytick.color":"#9aa3b5",
 "font.size":11,"grid.color":"#232733"})
V=[("BASELINE","no rollout at all",0,19380),
   ("A_immediate","exits on SIGTERM",51,19302),
   ("B_graceful","graceful shutdown",25,19392),
   ("C_prestop","+ preStop sleep 5",20,19308),
   ("D_drainconns","+ closes keep-alives",0,25884)]
fig=plt.figure(figsize=(12,8.4)); gs=fig.add_gridspec(2,1,height_ratios=[1,1.25],hspace=0.46)
ax=fig.add_subplot(gs[0])
cols=["#4a9eff","#e5484d","#e5484d","#e5484d","#3fb950"]
names=[f"{d}" for _,d,_,_ in V]; vals=[f for _,_,f,_ in V]
b=ax.barh(range(len(V)),vals,color=cols,edgecolor="#12141a",lw=1.5)
for i,(k,d,f,n) in enumerate(V):
    ax.text(f+0.8,i,f"{f} failed  of {n:,}",va="center",color="#e6e8ee",fontsize=10.5)
ax.set_yticks(range(len(V))); ax.set_yticklabels(names); ax.invert_yaxis()
ax.set_xlim(0,72); ax.set_xlabel("failed requests during one rolling update")
ax.grid(axis="x",alpha=.3,lw=.6)
ax.set_title("Same rollout, same load, four shutdown behaviours",loc="left",pad=10,fontsize=12.5)
ax2=fig.add_subplot(gs[1])
d=pathlib.Path("out/C_prestop")
reqs=json.load(open(d/"requests.json")); t0=min(r[0] for r in reqs)
ok=[(r[0]-t0,r[1]*1000) for r in reqs if r[2]==200]
bad=[(r[0]-t0,max(r[1]*1000,0.4)) for r in reqs if r[2]!=200]
sig=[float(m.group(1))-t0 for m in re.finditer(r"(\d+\.\d+) \S+ SIGTERM received",(d/"pods.log").read_text(errors="replace"))]
ax2.scatter(*zip(*ok),s=4,color="#4a9eff",alpha=.35,edgecolors="none",label="200 OK")
for i,s in enumerate(sig):
    ax2.axvline(s,color="#f5a524",ls="--",lw=1.2,alpha=.9,label="SIGTERM to a pod" if i==0 else None)
    ax2.axvspan(s,s+3.0,color="#f5a524",alpha=.07,lw=0)
ax2.scatter(*zip(*bad),s=46,color="#e5484d",marker="x",lw=2,label="connection dropped",zorder=5)
ax2.set_yscale("log"); ax2.set_xlim(20,52); ax2.grid(alpha=.3,lw=.6)
ax2.set_xlabel("seconds into the run"); ax2.set_ylabel("latency (ms, log)")
ax2.legend(loc="upper right",facecolor="#1a1d26",edgecolor="#3a4050",fontsize=9.5)
ax2.set_title("With preStop AND graceful shutdown: every failure lands 3.0s after a SIGTERM, when the pod finally exits",
              loc="left",pad=10,fontsize=11.5)
fig.suptitle("A rolling update with maxUnavailable: 0 still drops requests",x=0.065,ha="left",fontsize=14.5,y=0.985)
fig.text(0.065,0.948,"DOKS 1.36.3, 4 replicas behind a cloud load balancer, 20 keep-alive clients. Baseline without a rollout: 0 failures.",
         ha="left",fontsize=10,color="#9aa3b5")
fig.subplots_adjust(left=0.16,right=0.97,top=0.875,bottom=0.07)
fig.savefig("results.png",dpi=145); print("wrote results.png")
