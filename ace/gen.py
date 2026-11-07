import os, sys, time, json, traceback
sys.path.insert(0, "/tmp/ace")
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
jobs = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
t0 = time.time()
dit = AceStepHandler()
print(dit.initialize_service(project_root="/tmp/ace", config_path="acestep-v15-turbo", device="cpu"), flush=True)
llm = LLMHandler()
use_llm = os.environ.get("USE_LLM") == "1"
if use_llm:
    try:
        print(llm.initialize(checkpoint_dir="/tmp/ace/checkpoints", lm_model_path="acestep-5Hz-lm-0.6B", backend="pt", device="cpu"), flush=True)
    except Exception as e:
        print("LLM init failed", e); use_llm = False
print("init s", round(time.time() - t0), flush=True)
for j in jobs:
    t1 = time.time()
    try:
        p = GenerationParams(caption=j["caption"], lyrics=j["lyrics"], vocal_language="hi", duration=j["duration"],
                             bpm=j.get("bpm"), thinking=use_llm, inference_steps=8)
        c = GenerationConfig(batch_size=1, audio_format="wav")
        r = generate_music(dit, llm, p, c, save_dir=os.path.join(out, j["name"]))
        print(j["name"], "ok" if r.success else r.error, [a.get("path") for a in (r.audios or [])], "s", round(time.time() - t1), flush=True)
    except Exception:
        traceback.print_exc()
