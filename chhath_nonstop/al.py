import numpy as np,subprocess,json,sys
from faster_whisper import WhisperModel
m=WhisperModel('model/whisper_small',device='cpu',compute_type='int8')
P={'kanch':'काँच ही बाँस के बहँगिया, बहँगी लचकत जाय। होई ना बलम जी कहरिया, बहँगी घाटे पहुँचाय। बाट जे पूछेला बटोहिया, बहँगी केकरा के जाय। तू त आन्हर होवे रे बटोहिया, बहँगी छठी मइया के जाय। सूपवा में ठेकुआ सजल बा, दउरा में फल-फूल। छठी मइया के घाट चलीं, मिट जाई सब सूल।',
 'ghat_v1':'छठ के रौनक छठ के धूम, घाटे चलीं सब झूम झूम। सूप सजल बा ठेकुआ संगे, केला नरियर रंग बिरंगे। माई के दरबार सजल बा, घाट पे सब परिवार चलल बा। ढोल बाजे ढमा ढम, नाचे मनवा छम छम। जय छठी मैया जय छठी मैया, पार लगइहें हमरी नैया, सूरज देव के लीं बलैया। डूबत सूरज के अरघ दिहीं, उगत सूरज के पांव पड़ीं, दीया बाती जगमग जगमग, नदिया किनारे रौनक हरदम। बोल जय जय छठी माई, सबके घर में खुसी आई।'}
out={}
for n,pr in P.items():
  a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f'cn/{n}.wav','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
  segs,_=m.transcribe(a,language='hi',initial_prompt=pr,condition_on_previous_text=False,no_speech_threshold=0.9,log_prob_threshold=-3)
  out[n]=[(round(s.start,2),round(s.end,2),s.text) for s in segs]
json.dump(out,open('cn/align.json','w'),ensure_ascii=False,indent=0)
for n,v in out.items():
  print('==',n)
  for s in v: print(s)
