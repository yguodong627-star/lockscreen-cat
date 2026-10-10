"""Validate the cat (roasts.json, encouragements.json) and dog (roasts_dog.json,
encouragements_dog.json) libraries: structure, counts, lengths, placeholders,
duplicates within each file and across all four files, species words and
fur-colour words."""
import json,re,sys
D="/workspace/lockscreen-cat/"
SB=["<3000","3000-6000","6000-10000",">10000"]; BB=["23点前","23-1点","1点后"]
FILES=[("roasts.json","roasts"),("encouragements.json","encouragements"),
       ("roasts_dog.json","roasts"),("encouragements_dog.json","encouragements")]
LEGACY_WARN={"roasts.json"}  # only the legacy cat roasts file gets warnings instead of errors for >3 placeholder-free lines
FORBIDDEN_ALL=["橘","橙","奶黄","金毛"]                      # fur colour is not fixed: fail in any file
FORBIDDEN={"cat":["汪","狗"],"dog":["猫","喵","本猫","白","黄","红","项圈"]}  # species words; dog: no fur colour / collar
NOTE="used when sleep data is unavailable"
MAXLEN=30; GROUP_N=20; NOSLEEP_N=10; MAX_NONE_PER_GROUP=3  # strict for encouragements; roasts.json legacy lines only warned
errs=[]; warns=[]; global_seen={}

def check_line(l,where,allowed,fseen,stats,species):
    if not isinstance(l,str) or not l.strip(): errs.append(f"empty in {where}"); return
    for w in FORBIDDEN_ALL+FORBIDDEN[species]:
        if w in l: errs.append(f"forbidden word {w!r} ({species} file): {where}: {l}")
    if l!=l.strip(): errs.append(f"whitespace padding: {where}: {l!r}")
    bad=set(re.findall(r"\{[^}]*\}",l))-allowed
    if bad: errs.append(f"bad placeholder {bad}: {where}: {l}")
    if re.search(r"[{}]",re.sub(r"\{steps\}|\{bedtime\}","",l)): errs.append(f"stray brace: {where}: {l}")
    n=len(l.replace("{steps}","12345").replace("{bedtime}","01:47"))
    if n>MAXLEN: errs.append(f"too long ({n}): {where}: {l}")
    if l in fseen: errs.append(f"dup in file: {l} ({fseen[l]} & {where})")
    fseen[l]=where
    hs,hb="{steps}" in l,"{bedtime}" in l
    k="both" if hs and hb else "steps" if hs else "bedtime" if hb else "none"
    stats[k]+=1; return k

for fn,key in FILES:
    species="dog" if "_dog" in fn else "cat"
    try: d=json.load(open(D+fn,encoding="utf-8"))
    except Exception as e: errs.append(f"{fn}: cannot load: {e}"); continue
    exp_keys=["version","placeholders","step_buckets","bedtime_buckets",key,"no_sleep_data","no_sleep_data_bucket_note"]
    if list(d)!=exp_keys: errs.append(f"{fn}: top-level keys {list(d)} != {exp_keys}")
    if d.get("version")!=1: errs.append(f"{fn}: version")
    if d.get("placeholders")!=["{steps}","{bedtime}"]: errs.append(f"{fn}: placeholders")
    if d.get("step_buckets")!=SB: errs.append(f"{fn}: step_buckets")
    if d.get("bedtime_buckets")!=BB: errs.append(f"{fn}: bedtime_buckets")
    if d.get("no_sleep_data_bucket_note")!=NOTE: errs.append(f"{fn}: no_sleep_data_bucket_note")
    fseen={}; stats={"steps":0,"bedtime":0,"both":0,"none":0}; ns={"steps":0,"bedtime":0,"both":0,"none":0}
    r=d.get(key,{})
    if not isinstance(r,dict) or list(r)!=SB: errs.append(f"{fn}: {key} keys {list(r) if isinstance(r,dict) else r}")
    main=0
    for s in SB:
        g=r.get(s,{}) if isinstance(r,dict) else {}
        if not isinstance(g,dict) or list(g)!=BB: errs.append(f"{fn}: {key}/{s} keys"); continue
        for b in BB:
            L=g[b]
            if not isinstance(L,list) or len(L)!=GROUP_N: errs.append(f"{fn}: {s}/{b} count {len(L) if isinstance(L,list) else L}"); continue
            none=0
            for l in L:
                main+=1
                if check_line(l,f"{fn}:{key}/{s}/{b}",{"{steps}","{bedtime}"},fseen,stats,species)=="none": none+=1
            if none>MAX_NONE_PER_GROUP: (warns if fn in LEGACY_WARN else errs).append(f"{fn}: {s}/{b} has {none} lines without placeholders (>{MAX_NONE_PER_GROUP})")
    nsd=d.get("no_sleep_data",{}); nsl=0
    if not isinstance(nsd,dict) or list(nsd)!=SB: errs.append(f"{fn}: no_sleep_data keys {list(nsd) if isinstance(nsd,dict) else nsd}")
    else:
        for s in SB:
            L=nsd[s]
            if not isinstance(L,list) or len(L)!=NOSLEEP_N: errs.append(f"{fn}: no_sleep_data/{s} count"); continue
            for l in L:
                nsl+=1
                if isinstance(l,str) and "{bedtime}" in l: errs.append(f"{fn}: {{bedtime}} in no_sleep_data/{s}: {l}")
                check_line(l,f"{fn}:no_sleep_data/{s}",{"{steps}"},fseen,ns,species)
    for l,w in fseen.items():
        if l in global_seen: errs.append(f"cross-file dup: {l} ({global_seen[l]} & {w})")
        global_seen.setdefault(l,w)
    print(f"{fn}: {key}={main} lines, no_sleep_data={nsl} lines, unique in file={len(fseen)}")
    print(f"  {key} placeholder mix: {stats}")
    print(f"  no_sleep_data placeholder mix: {ns}")
print(f"total lines across files: {len(global_seen)} unique")
[print(" warn:",w) for w in warns]
if errs: print("FAIL"); [print(" -",e) for e in errs]; sys.exit(1)
print("PASS")
