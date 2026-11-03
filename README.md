# toolkit (backup of session-only editing tools, 3 Nov 2026)
Restore in a new chat: git clone -b toolkit <repo> ; set S=<scratch>; copy libs/*.py to $S/work/ ; fonts/*.ttf to $S/fonts/ ; brand/* to $S/brand/ ;
whisper: cat whisper_small_parts/model.bin.part* > $S/model/whisper_small/model.bin (+ copy the json files).
Scripts hardcode old scratchpad path S=...b66cce68...; change S at top of each script.
libs: ralib/hmlib/smlib/svlib/rslib/lmlib/kplib = ribbon(), rich(), subtitle + shot helpers. ghat_chali/edit_flow.py+build_flow.py = latest long+native-9:16 Shorts pipeline (clean-window clips + Ken Burns). chhath_nonstop/subs.py = subtitle overlay.
Python deps: pillow, numpy, opencv(ORB), faster-whisper, ffmpeg.
