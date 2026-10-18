import json,sys,statistics as st,collections
for n in sys.argv[1:]:
    try: R=json.load(open(f'res_{n}.json'))
    except Exception as e: print(n,'ERR',e); continue
    w=sum(1 for r in R if r.get('wonRun') or r['result']=='win')
    words=[len(r['words']) for r in R]
    lens=collections.Counter(min(x['len'],8) for r in R for x in r['words']); tot=sum(lens.values())
    fr=collections.Counter(r['finalRound'] for r in R if not (r.get('wonRun') or r['result']=='win'))
    stuck=sum(1 for r in R if r['_sim'].get('ended')=='stuck')
    p=w/len(R)
    ch=[c for r in R for c in (r.get('challenges') or []) if c.get('taken')]
    cl=sum(1 for c in ch if c.get('cleared')); chs=f" chal={cl}/{len(ch)}={cl/max(1,len(ch)):.0%}"
    byt=collections.defaultdict(lambda:[0,0])
    for c in ch: byt[c['type']][1]+=1; byt[c['type']][0]+=1 if c.get('cleared') else 0
    chs+=" "+" ".join(f"{k}:{a}/{b}" for k,(a,b) in sorted(byt.items()))
    print(f"{n:24s} n={len(R)} win={p:.0%} (±{(p*(1-p)/len(R))**.5:.0%}) stuck={stuck} words/run={st.mean(words):.1f} len={{{', '.join(f'{k}:{v/tot:.0%}' for k,v in sorted(lens.items()))}}} lost_in={dict(sorted(fr.items()))}{chs}")
