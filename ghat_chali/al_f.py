import numpy as np,subprocess,json
from faster_whisper import WhisperModel
m=WhisperModel('model/whisper_small',device='cpu',compute_type='int8')
pr='भोरे भोरे घाट चलीं, सूप सजा के हाथ चलीं, ठेकुआ केला नरियर लेके, छठी मैया के साथ चलीं। जय जय छठी मैया, जय हो सूरज देव, अरघ देवे आइल बानी, किरपा करीं सदैव। नहाय खाय से व्रत शुरू, खरना के प्रसाद बने, तीन दिन के निर्जल पूजा, मैया के आशीष घने। सांझ के अरघ डूबत सूरज, जल में ठाढ़ व्रती सब, दीया बाती गीत सुहावन, घाट सजल बा अब। भोर के अरघ उगत सूरज, लाल किरन बरसाय, गोदी भरल रहे सबके, घर में सुख समाय।'
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','gc/song_flow.wav','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs,_=m.transcribe(a,language='hi',initial_prompt=pr,condition_on_previous_text=False,no_speech_threshold=0.9,log_prob_threshold=-3,word_timestamps=True)
out=[]
for s in segs:
  print(round(s.start,1),round(s.end,1),s.text,flush=True)
  out.append((s.start,s.end,s.text,[(w.start,w.end,w.word) for w in s.words]))
json.dump(out,open('gc/align_flow.json','w'),ensure_ascii=False)
