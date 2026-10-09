import json, gzip, os, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
SURF="#1a1a19"; T1="#ffffff"; T2="#c3c2b7"; GRID="#2e2d2a"; OLD="#3987e5"; NEW="#d95926"; CRIT="#d03b3b"
plt.rcParams.update({"figure.facecolor":SURF,"axes.facecolor":SURF,"text.color":T1,"axes.labelcolor":T2,
  "xtick.color":T2,"ytick.color":T2,"axes.edgecolor":GRID,"font.size":11,"font.family":"DejaVu Sans"})
runs=[("D2_immediate","3","4","Default settings",84.0),("D3_drain60","5","6","With termination.drain_seconds: 60",None)]
fig,axes=plt.subplots(2,1,figsize=(13,10),sharex=True)
for ax,(L,old,new,title,death) in zip(axes,runs):
    fast=(json.load(gzip.open(f"out/{L}/requests.json.gz")) if os.path.exists(f"out/{L}/requests.json.gz") else json.load(open(f"out/{L}/requests.json"))); t0=min(x[0] for x in fast)
    Z=min(x[0] for x in fast if x[2]==200 and x[3].endswith(f"gen={new}"))
    l_old=max(x[0] for x in fast if x[2]==200 and x[3].endswith(f"gen={old}"))-Z
    slow=sorted(json.load(open(f"out/{L}/slow.json")),key=lambda s:s["start"])
    sel=[s for s in slow if -21<=s["start"]-Z<=32]; fails=[]
    for i,s in enumerate(sel):
        x0=s["start"]-Z; x1=s["end"]-Z
        if s["status"]!=200:
            ax.plot([x0,x1],[i,i],color=CRIT,lw=2.2,solid_capstyle="butt"); ax.plot(x1,i,"x",color=CRIT,ms=8,mew=2.2); fails.append((x1,i))
        else:
            ax.plot([x0,x1],[i,i],color=OLD if f"gen={old}" in s["body"] else NEW,lw=2.2,solid_capstyle="butt")
    n=len(sel)
    ax.axvspan(0,l_old,color=T2,alpha=0.09,lw=0); ax.axvline(l_old,color=T2,ls=":",lw=1.4)
    ax.text(l_old/2,n+0.6,f"both versions\nanswering {l_old:.1f} s",ha="center",va="top",fontsize=9.6,color=T2)
    if death:
        dz=t0+death-Z
        ax.axvline(dz,color=CRIT,ls="--",lw=1.6)
        ax.annotate("",xy=(dz,n+1.0),xytext=(l_old,n+1.0),arrowprops=dict(arrowstyle="<->",color=T1,lw=1.2))
        ax.text((l_old+dz)/2,n+1.6,f"old version kept alive {dz-l_old:.1f} s",ha="center",fontsize=10,color=T1)
        fx,fy=max(fails)
        ax.text(fx+1.0,fy,f"{len(fails)} requests cut off (504)",color=T1,fontsize=10,va="center",fontweight="bold")
        ax.text(dz+0.6,2,"old container\nstopped",color=T1,fontsize=9.5)
    ax.set_ylim(-2,n+5); ax.set_yticks([])
    ax.grid(axis="x",color=GRID,lw=0.8); ax.set_axisbelow(True)
    for sp in ("top","right","left"): ax.spines[sp].set_visible(False)
    tot=len(slow); nf=sum(1 for s in slow if s["status"]!=200)
    ax.set_title(f"{title}: {tot-nf} of {tot} twenty-second requests completed",loc="left",fontsize=12.5,color=T1,pad=6)
axes[0].set_xlim(-22,56); axes[1].set_xlabel("seconds after the new version's first response")
h=[Line2D([0],[0],color=OLD,lw=4,label="finished by the old version"),
   Line2D([0],[0],color=NEW,lw=4,label="finished by the new version"),
   Line2D([0],[0],color=CRIT,lw=4,marker="x",ms=8,mew=2,label="cut off with a 504")]
fig.legend(handles=h,loc="lower center",bbox_to_anchor=(0.5,0.005),ncol=3,frameon=False,fontsize=10.5,labelcolor=T2)
fig.text(0.012,0.982,"One line per 20-second request, held open across an App Platform redeploy",fontsize=14.5,color=T1,va="top")
fig.text(0.012,0.950,"After the dotted line the old version gets no new requests, but it stays up to finish the ones it already has.",fontsize=10.5,color=T2,va="top")
fig.subplots_adjust(left=0.02,right=0.985,top=0.885,bottom=0.115,hspace=0.30)
fig.savefig("fig_cutover.png",dpi=130)
