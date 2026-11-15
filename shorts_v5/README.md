# Shorts V5 — Lakshmi/festival Shorts editing style (15 Nov 2026)
Branch: `toolkit-shorts-v5`. Fonts + logo: branch `toolkit` (tk/fonts, tk/brand/logo_512q.png). Paths in the scripts assume /home/claude/work/v5 (+ ../sh narration/BGM) — change B/SH at the top of compose.py.

## Files
- `compose.py` — build(): per-scene segments (pic: 2160x3840 zoompan 1->1.045 @30fps; clip: trim + scale + tpad clone), concat, burned captions, logo top-left, end card, audio mix, final mux. TAIL=4.0 s.
- `run_all.py` — scene + sentence timing for S1..S5 (`python3 -I run_all.py 1 2 3 4 5`).
- `lib/cards.py` — caption_png (white Tiro Devanagari 72px, stroke 4, dark rounded band at y~1560, maxw 960) and card_on_bg (text cards for mantra/date/time).
- `upload/make_batch.py`, `upload/meta.json` — titles/descriptions/slots -> upload/<name> branch batch (manifest LAST).

## Style rules (user's)
1. Story Shorts: the goddess herself is IN the house, looking at each situation (quarrel, dirty dishes, ignored elder, wasted food, laziness) — reference Shorts mreNbuGgTTc, XgAV-OwSlzw.
2. No still/card longer than ~5.5 s; mix of pics + real clips (hybrid).
3. Captions: big white, bottom band, split <=26 chars/chunk; Tiro Devanagari only (Yatra breaks anusvara).
4. Spoken CTA at the END of every narration, same voice: "सनातन बीट्स से जुड़े रहने के लिए, कृपया लाइक और सब्सक्राइब करें, और घंटी का बटन दबाएँ।" + on-screen end card (logo, red "सब्सक्राइब करें", "लाइक · कमेंट · शेयर") from CTA start; text never on the face.
5. BGM must not die with the voice: BGM trimmed to narration+TAIL, sidechain ducking, fade only the last 2 s.
6. Mix: voice loudnorm -15 + apad; BGM dynaudnorm + loudnorm -29, +3 dB, sidechaincompress 0.08/2/20/400; amix normalize=0, +2 dB, alimiter 0.85; final -1.5 dB => -14.3..-15.0 LUFS.
7. QC: ebur128, freezedetect, blackdetect, contact sheets of frames vs spoken sentence; Claude cannot hear — user judges audio by ear.
