import sys,json,time,urllib.request,urllib.parse,collections,string
name=sys.argv[1]; d=f"kwr/{name}"
seeds=[l.strip() for l in open(f"{d}/seeds.txt",encoding="utf-8") if l.strip()]
suf=["","कथा","कहानी","जन्म कथा","कब","क्यों","क्या","सुनाइए","पूरी कथा","katha","kahani","janm katha","story","2026","भजन","full video","hindi","रहस्य","कैसे हुआ","कौन थे"]
hi="कखगघचछजटठडतथदनपफबभमयरलवशसह"
res=collections.OrderedDict(); freq=collections.Counter(); err=[]
def sug(q,hl):
    u="https://suggestqueries.google.com/complete/search?"+urllib.parse.urlencode({"client":"firefox","ds":"yt","hl":hl,"gl":"in","q":q})
    for _ in range(2):
        try: return json.loads(urllib.request.urlopen(u,timeout=15).read().decode("utf-8","ignore"))[1]
        except Exception as e: e_=str(e)[:100]; time.sleep(1)
    err.append(f"{q}|{e_}"); return []
for s in seeds:
    qs=[s]+[f"{s} {x}" for x in suf if x]+[f"{s} {c}" for c in string.ascii_lowercase+hi]
    for q in qs:
        for hl in ("hi","en"):
            r=sug(q,hl); res[f"{hl}|{q}"]=r
            for i,t in enumerate(r): freq[t]+=1
            time.sleep(0.12)
json.dump({"seeds":seeds,"top":freq.most_common(400),"raw":res,"errors":err[:50]},open(f"{d}/out.json","w"),ensure_ascii=False)
print(len(freq),"unique;",len(err),"errors")
