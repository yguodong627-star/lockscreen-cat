import json,re,sys
SB=["<3000","3000-6000","6000-10000",">10000"]; BB=["23点前","23-1点","1点后"]
errs=[]
d=json.load(open("/workspace/lockscreen-cat/roasts.json",encoding="utf-8"))
if d.get("version")!=1: errs.append("version")
if d.get("placeholders")!=["{steps}","{bedtime}"]: errs.append("placeholders")
if d.get("step_buckets")!=SB: errs.append("step_buckets")
if d.get("bedtime_buckets")!=BB: errs.append("bedtime_buckets")
r=d.get("roasts",{})
if set(r)!=set(SB): errs.append(f"roasts keys {list(r)}")
seen={}; total=0; stats={"steps":0,"bedtime":0,"both":0,"none":0}
for s in SB:
  if set(r.get(s,{}))!=set(BB): errs.append(f"{s} keys"); continue
  for b in BB:
    L=r[s][b]
    if len(L)!=20: errs.append(f"{s}/{b} count {len(L)}")
    for l in L:
      total+=1
      if not isinstance(l,str) or not l.strip(): errs.append(f"empty in {s}/{b}"); continue
      bad=set(re.findall(r"\{[^}]*\}",l))-{"{steps}","{bedtime}"}
      if bad or re.search(r"[{}]",re.sub(r"\{steps\}|\{bedtime\}","",l)): errs.append(f"bad placeholder: {l}")
      n=len(l.replace("{steps}","12345").replace("{bedtime}","01:47"))
      if n>30: errs.append(f"too long ({n}): {s}/{b}: {l}")
      if l in seen: errs.append(f"dup: {l} ({seen[l]} & {s}/{b})")
      seen[l]=f"{s}/{b}"
      hs,hb="{steps}" in l,"{bedtime}" in l
      stats["both" if hs and hb else "steps" if hs else "bedtime" if hb else "none"]+=1
print(f"total lines: {total}, unique: {len(seen)}, placeholder mix: {stats}")
if errs: print("FAIL"); [print(" -",e) for e in errs]; sys.exit(1)
print("PASS")
