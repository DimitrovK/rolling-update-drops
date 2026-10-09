import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
SURF="#1a1a19"; T1="#ffffff"; T2="#c3c2b7"; GRID="#2e2d2a"
C=["#3987e5","#d95926","#199e70"]
plt.rcParams.update({"figure.facecolor":SURF,"axes.facecolor":SURF,"text.color":T1,"axes.labelcolor":T2,
  "xtick.color":T2,"ytick.color":T2,"axes.edgecolor":GRID,"font.size":11,"font.family":"DejaVu Sans"})
def phases(L):
    ev=[l.split() for l in open(f"out/{L}/events.log")]; t0=float(ev[0][0]); p={}
    for e in ev:
        if len(e)>2 and e[1]=="PHASE" and len(e)>=4: p.setdefault(e[3],float(e[0])-t0)
    return p
rows=[("deploy 1","D1_immediate"),("deploy 2","D2_immediate"),("deploy 4","D4_default_repeat"),("deploy 3, drain 60 s","D3_drain60")]
fig,ax=plt.subplots(figsize=(12,4.6))
for i,(lab,L) in enumerate(rows):
    p=phases(L); segs=[("waiting to build",p["PENDING_BUILD"],p["BUILDING"]),
                       ("building",p["BUILDING"],p["DEPLOYING"]),("deploying",p["DEPLOYING"],p["ACTIVE"])]
    for j,(name,a,b) in enumerate(segs):
        ax.barh(i,b-a-0.25,left=a,color=C[j],height=0.58,edgecolor=SURF,lw=0)
    ax.text(p["ACTIVE"]+0.8,i,f"active at {p['ACTIVE']:.1f} s",va="center",fontsize=10.5,color=T1)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows]); ax.invert_yaxis()
ax.set_xlim(0,88); ax.set_xlabel("seconds after submitting the change")
ax.grid(axis="x",color=GRID,lw=0.8); ax.set_axisbelow(True)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C[0],label="waiting to build"),Patch(color=C[1],label="building"),Patch(color=C[2],label="deploying")],
          loc="lower right",bbox_to_anchor=(1.0,1.01),ncol=3,frameon=False,labelcolor=T2,fontsize=10)
ax.set_title("How long each redeploy took to go live",loc="left",fontsize=13,color=T1,pad=10)
fig.subplots_adjust(left=0.17,right=0.97,top=0.82,bottom=0.15)
fig.savefig("fig_phases.png",dpi=130)
