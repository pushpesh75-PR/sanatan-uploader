import numpy as np,subprocess,json
from faster_whisper import WhisperModel
m=WhisperModel('model/whisper_small',device='cpu',compute_type='int8')
pr='ॐ एहि सूर्य सहस्रांशो तेजोराशे जगत्पते। अनुकम्पय मां भक्त्या गृहाणार्घ्यं दिवाकर।'
a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','cn/arghya.wav','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs,_=m.transcribe(a,language='hi',initial_prompt=pr,condition_on_previous_text=False,no_speech_threshold=0.9,log_prob_threshold=-3,word_timestamps=True)
out=[]
for s in segs:
  print(round(s.start,1),round(s.end,1),s.text,flush=True)
  out.append((s.start,s.end,s.text,[(w.start,w.end,w.word) for w in s.words]))
json.dump(out,open('cn/align_arg.json','w'),ensure_ascii=False)
