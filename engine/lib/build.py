"""Sync a WakilSmart reel to its ElevenLabs voiceover and render it.
usage: python3 -I build.py <reel4|reel5|...> <voice.mp3> [out.mp4]
Transcribes the voice, finds cue words, mixes music/SFX under the voice, renders."""
import sys, json, wave, subprocess, os, re
import numpy as np
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reel, voice = sys.argv[1], os.path.abspath(sys.argv[2])
out = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.path.join(ROOT, reel, f"wakilsmart_{reel}.mp4")
D_REEL = os.path.join(ROOT, reel)
SR = 44100

# cue word patterns per reel (first match after previous cue)
CUES = {
    "reel5": [("m1", r"الخط"), ("m2", r"الخط"), ("m3", r"الخط"), ("sol", r"الحل")],
    "reel4": [("r1", r"الجول|جولة"), ("e1", r"الموظف"), ("h1", r"الوكيل"), ("r2", r"الجول|جولة"), ("e2", r"الموظف"), ("h2", r"الوكيل"), ("r3", r"الجول|جولة"), ("e3", r"الموظف"), ("h3", r"الوكيل"),
              ("ko", r"ضرب|القاضي"), ("win", r"الفا|واضح")],
}
CUES["reel6"] = [("off", r"ظرف|كان"), ("night", r"آخر|وآخر|الليل"), ("bk", r"حجوز"), ("q", r"سؤال|وكل"), ("angry", r"حتى|معص"), ("dn", r"هدا|حجز"), ("end", r"خل|وكيلك")]
CUES["talk9"] = CUES_T9 = [("ans", r"جاوب|بصراح"), ("said", r"قال"), ("tw", r"بس|بعدها"), ("qt", r"الذكاء"), ("end", r"تخاف|فلا")]
CUES["reel9"] = [("ans", r"جاوب|بصراح"), ("said", r"قال"), ("tw", r"بس|بعدها"), ("qt", r"الذكاء"), ("end", r"تخاف|فلا")]
CUES["reel8"] = [("s1", r"أول|اول"), ("s2", r"ثاني"), ("s3", r"ثالث"), ("d2", r"يومين"), ("f", r"الوكيل"), ("bk", r"حجز"), ("end", r"موظف")]
SFX_HITS = {"talk9": lambda c: [c["ans"]], "reel9": lambda c: [c["ans"]], "reel6": lambda c: [c["bk"]], "reel8": lambda c: [c["bk"]], "reel4": lambda c: [c["h1"] + 0.55, c["h2"] + 0.55, c["h3"] + 0.55], "reel5": lambda c: []}

# 1) transcribe
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-ac", "1", "-ar", "16000", "/tmp/_v16.wav"], check=True)
w = wave.open("/tmp/_v16.wav"); a16 = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel("/home/claude/models/small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a16, language="ar", beam_size=5, word_timestamps=True)
words = [(x.start, x.end, x.word.strip()) for s in segs for x in s.words]
print(" ".join(f"{t:.1f}:{wd}" for t, _, wd in words))
dur = len(a16) / 16000

cues, last = {}, 0.0
for name, pat in CUES[reel]:
    hit = next((s for s, e, wd in words if s >= last and re.search(pat, wd)), None)
    if hit is None:
        raise SystemExit(f"cue {name} ({pat}) not found — check transcript")
    cues[name] = max(0, hit - 0.15); last = hit + 0.2

# yalla = onset of the final spoken burst (energy-based)
env = np.array([np.sqrt(np.mean(a16[i:i + 400] ** 2)) for i in range(0, len(a16) - 400, 160)])
thr = env.max() * 0.08
voiced = env > thr
end_i = len(voiced) - 1 - np.argmax(voiced[::-1])
i = end_i
while i > 0 and (voiced[i] or voiced[max(0, i - 8):i].any()): i -= 1
cues["A"] = round(max(cues[list(cues)[-1]] + 1.0, i * 0.01 - 0.05), 2)
cues["D"] = round(max(dur, cues["A"] + 2.2), 2)
# per-frame (30fps) voice envelope + "roundness" for lip-sync
hop = 16000 // 30; fr = []
for k in range(int(dur * 30) + 1):
    x = a16[k * hop:k * hop + 2 * hop]
    if len(x) < 10: fr.append((0, 0)); continue
    zc = np.mean(np.abs(np.diff(np.sign(x)))) / 2
    fr.append((float(np.sqrt(np.mean(x ** 2))), float(zc)))
pk = np.percentile([r for r, _ in fr if r > 0], 95) or 1
cues["env"] = [round(min(1, r / pk), 2) for r, _ in fr]
cues["zc"] = [round(z, 3) for _, z in fr]
print("cues", {k: v for k, v in cues.items() if k not in ("env", "zc")})
json.dump(cues, open(os.path.join(D_REEL, "cues.json"), "w"))

# 2) audio mix
D = cues["D"]; N = int(SR * D); mix = np.zeros(N)
def add(sig, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i < N: mix[i:j] += sig[:j - i] * g
def env_(n, a=0.005, r=None):
    t = np.arange(n) / SR; e = np.minimum(1, t / a)
    return e * np.exp(-t / r) if r else e
def tone(f, d, r=0.15, a=0.004, sq=False):
    n = int(d * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(f(t) if callable(f) else f, (n,))) / SR
    s = np.sign(np.sin(ph)) * 0.5 if sq else np.sin(ph)
    return s * env_(n, a, r)
def noise(d, r=0.1): n = int(d * SR); return np.random.randn(n) * env_(n, 0.01, r)
def whoosh(d=0.45):
    n = int(d * SR); t = np.linspace(0, 1, n)
    return np.convolve(np.random.randn(n), np.ones(12) / 12, "same") * np.sin(np.pi * t) ** 2 * 1.4
def pop():
    s = tone(lambda t: 900 - 2500 * t, 0.09, 0.03); s[:2205] += tone(1600, 0.05, 0.015) * 0.3; return s
def chime():
    s = np.zeros(int(0.9 * SR))
    for k, f in enumerate([784, 988, 1175, 1568]):
        x = tone(f, 0.6, 0.2) * 0.4; i = int(k * 0.08 * SR); s[i:i + len(x)] += x[:len(s) - i]
    return s
def punch():
    s = tone(lambda t: 140 * np.exp(-t * 18) + 50, 0.35, 0.1) * 1.2; s[:int(0.08 * SR)] += noise(0.08, 0.02)[:int(0.08 * SR)] * 0.6; return s
kick = tone(lambda t: 120 * np.exp(-t * 25) + 45, 0.35, 0.12) * 0.9
hat = noise(0.05, 0.012) * 0.18
snare = noise(0.18, 0.05) * 0.35
beat = 60 / 112; t = 0.0; b = 0
while t < cues["A"] - 0.3:
    if b % 4 in (0, 2): add(kick, t)
    if b % 4 in (1, 3): add(snare, t, 0.8)
    add(hat, t + beat / 2); add(hat, t, 0.6)
    if b % 2 == 0: add(tone([55, 55, 65.4, 49][(b // 4) % 4], beat * 1.8, 0.4) * 0.35, t)
    t += beat; b += 1
mix *= 0.5
for k, v in cues.items():
    if k in ("env", "zc"): continue
    if k in ("A", "D", "d2", "f", "bk", "dn") or k[0] in "eh" and k[1:].isdigit(): continue
    add(whoosh(), max(0, v - 0.1), 0.6); add(pop(), v + 0.4, 0.6)
for h in SFX_HITS[reel](cues): add(punch(), h, 1.0)
if "ko" in cues: add(punch(), cues["ko"], 1.6); add(punch(), cues["ko"] + 0.3, 1.4)
add(chime(), [v for k, v in cues.items() if k not in ("env", "zc")][-3] + 0.3, 0.6)
A = cues["A"]; add(whoosh(0.3), A - 0.25, 0.9); add(kick, A, 1.6); add(chime(), A + 0.05, 1.2); add(noise(0.6, 0.25) * 0.25, A)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-ac", "1", "-ar", str(SR), "/tmp/_vo.wav"], check=True)
vw = wave.open("/tmp/_vo.wav"); v = np.frombuffer(vw.readframes(vw.getnframes()), np.int16).astype(float) / 32768
v = v / np.max(np.abs(v)) * 0.9; vv = np.zeros(N); vv[:min(N, len(v))] = v[:N]
ev = np.convolve(np.abs(vv), np.ones(4410) / 4410, "same"); duck = 1 - 0.55 * np.clip(ev / 0.05, 0, 1)
mix = mix / np.max(np.abs(mix)) * 0.55 * duck + vv
mix /= np.max(np.abs(mix)) * 1.05
fade = int(0.4 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
aw = os.path.join(D_REEL, "audio.wav")
ww = wave.open(aw, "wb"); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((mix * 32767).astype(np.int16).tobytes()); ww.close()

# 3) render
subprocess.run(["node", os.path.join(ROOT, "lib", "render.js"), D_REEL, os.path.join(D_REEL, "cues.json"), aw, out], check=True)
print("done", out)
