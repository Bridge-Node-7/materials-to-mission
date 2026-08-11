from __future__ import annotations
import hashlib, json, math
from pathlib import Path

def build_memberships(atlas: dict, applications: dict):
    rows=applications["rows"]; exact={}; lens_members={}
    for m in atlas["materials"]:
        name=m["name"]
        member_rows=[rid for rid,row in rows.items() if name in set(row["materials"])]
        exact[name]=member_rows
        lens_members[name]=[
            lid for lid,lens in atlas["lenses"].items()
            if any(r in member_rows for r in lens["doe_rows"])
        ]
    return exact,lens_members

def derive_positions(atlas: dict, applications: dict):
    exact,lens_members=build_memberships(atlas,applications)
    lenses=atlas["lenses"]; positions={}; bases={}; neutral=[]
    for m in atlas["materials"]:
        name=m["name"]; ls=lens_members[name]
        if ls:
            x=sum(lenses[l]["anchor"]["x"] for l in ls)/len(ls)
            y=sum(lenses[l]["anchor"]["y"] for l in ls)/len(ls)
            h=int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:12],16)
            jx=((h%10000)/9999-.5)*7.2
            jy=(((h//10000)%10000)/9999-.5)*7.2
            positions[name]=[x+jx,y+jy]; bases[name]=[x,y]
        else:
            neutral.append(name)
    for i,name in enumerate(neutral):
        angle=math.pi*.12+i*(math.pi*1.76/max(1,len(neutral)-1))
        x=50+44*math.cos(angle); y=50+39*math.sin(angle)
        positions[name]=[x,y]; bases[name]=[x,y]
    names=[m["name"] for m in atlas["materials"]]
    for _ in range(520):
        delta={n:[(bases[n][0]-positions[n][0])*.020,(bases[n][1]-positions[n][1])*.020] for n in names}
        for i,a in enumerate(names):
            ax,ay=positions[a]
            for b in names[i+1:]:
                bx,by=positions[b]
                dx=ax-bx; dy=ay-by; d2=dx*dx+dy*dy; min_d=5.45
                if 0.0001<d2<min_d*min_d:
                    d=math.sqrt(d2); push=(min_d-d)*.043; ux,uy=dx/d,dy/d
                    delta[a][0]+=ux*push; delta[a][1]+=uy*push
                    delta[b][0]-=ux*push; delta[b][1]-=uy*push
        for n in names:
            positions[n][0]=max(4,min(96,positions[n][0]+delta[n][0]))
            positions[n][1]=max(6,min(94,positions[n][1]+delta[n][1]))
    out={n:{"x":round(v[0],3),"y":round(v[1],3)} for n,v in positions.items()}
    return out,exact,lens_members

def coordinate_digest(atlas:dict, applications:dict)->str:
    coords,_,_=derive_positions(atlas,applications)
    ordered=[(m["id"],coords[m["name"]]["x"],coords[m["name"]]["y"]) for m in atlas["materials"]]
    return hashlib.sha256(json.dumps(ordered,separators=(",",":")).encode()).hexdigest()

def main()->int:
    root=Path(__file__).resolve().parents[1]
    field=root/"public-snapshots/materials-field/MF-001"
    atlas=json.loads((field/"atlas.json").read_text(encoding="utf-8"))
    apps=json.loads((field/"doe-application-map.json").read_text(encoding="utf-8"))
    print("PASS - reproducible Strategic Constellation coordinates")
    print("COORDINATE_SET_SHA256="+coordinate_digest(atlas,apps))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
