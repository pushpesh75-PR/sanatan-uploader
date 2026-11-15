import json,os,shutil,subprocess,sys
meta=json.load(open("/home/claude/work/up/meta.json"))
V="/home/claude/work/v5/build/"
D="/home/claude/sanatan-uploader/batch"
shutil.rmtree(D,ignore_errors=True); os.makedirs(D)
files={"lakshmi-alakshmi-katha-short":"S1_j.mp4","lakshmi-ghar-se-kab-jati-short":"S2_j.mp4","shukrawar-lakshmi-puja-short":"S3_j.mp4","kartik-purnima-kab-hai-short":"S4_j.mp4","dev-deepawali-deepdaan-short":"S5_j.mp4"}
pl={"lakshmi":"माँ लक्ष्मी | Maa Lakshmi Shorts","kp":"कार्तिक पूर्णिमा और देव दीपावली 2026"}
items=[]
for m in meta:
    k=m["key"]; fn=k+".mp4"
    src=V+files[k]; sz=os.path.getsize(src)
    assert sz<90*1024*1024
    shutil.copy(src,D+"/"+fn+".part000")
    items.append(dict(key=k,file=fn,title=m["title"],description=m["desc"],tags=[],publish_at_utc=m["slot"],category_id="10",language="hi",synthetic=True,
      location=dict(lat=20.5937,lng=78.9629,desc="India"),
      playlists=[pl["lakshmi"] if "lakshmi" in k or "shukrawar" in k else pl["kp"]]))
json.dump({"items":items},open(D+"/manifest.json","w"),ensure_ascii=False,indent=1)
open(D+"/approved.txt","w").write("\n".join(i["key"] for i in items)+"\n")
print([ (i["key"],len(i["title"]),i["publish_at_utc"]) for i in items])
