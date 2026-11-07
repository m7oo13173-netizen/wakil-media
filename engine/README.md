# WakilSmart reel engine
HTML/JS animation engine for WakilSmart.ai reels (1080x1920, 30fps) + auto-sync to an ElevenLabs voiceover.

Layout expected at runtime (`$W` = working dir, e.g. /home/claude/wakil-content):
- `$W/lib/`      ← engine/lib (lib.js, base.css, render.js, build.py, cover/story generators)
- `$W/mascot/`   ← engine/mascot (8 green-screen-keyed poses + 2 original sheets)
- `$W/fonts/`    ← `npm pack @fontsource/cairo@5.0.13` extracted as fontsource-cairo-5.0.13
- `$W/reelN/reel.html` ← one reel (see engine/examples); `$W/voices/*.mp3`
- Whisper small (CTranslate2) from npm: @skillninja/shortmovie-telop-model-p0..p3 → cat model.bin.part* > model.bin (set WHISPER_DIR)

Build: `cd $W/lib && python3 -I build.py reelN ../voices/x.mp3` (add CUES["reelN"] keyword patterns in build.py first).
