"""Saoud SFX Pack (CC0) — role-based random picker so every reel sounds different.
Usage:
    from sfxpack import Pack
    P = Pack(seed='reel-name')          # same seed -> same picks, new seed -> new mix
    M.add(P.get('whoosh'), t, .25)      # numpy mono @44100, peak-normalized
Roles: whoosh, swipe, hit, punch, boom, riser, downlifter, swell, pop, click, type, tick,
       success, confirm, ding, error, glitch, tech, laser, coin, cash, paper, step, jingle
"""
import os, json, random, subprocess, re
import numpy as np
SR = 44100
ROOT = os.path.dirname(os.path.abspath(__file__))
ROLES = {
 'whoosh':     [('transitions', r'^whoosh')],
 'swipe':      [('transitions', r'^(swipe|zip)')],
 'hit':        [('impacts', r'impact_impact_(punch|soft|plate)_(medium|heavy)|^impact(_2|_soft.*)?\.mp3')],
 'punch':      [('impacts', r'punch')],
 'boom':       [('impacts', r'^(boom|bass_drop|sci_low_frequency|hit)')],
 'riser':      [('risers', r'^(riser|air_swell)')],
 'downlifter': [('risers', r'^downlifter')],
 'swell':      [('risers', r'^reverse_swell')],
 'pop':        [('ui', r'^(ui_click|interface_pluck|interface_drop|interface_open|soft_tick|swap_tick)')],
 'click':      [('ui', r'^(ui_click|interface_click|ui_mouseclick|interface_select|interface_toggle)')],
 'type':       [('ui', r'^(type_tick|key_press|typing)')],
 'tick':       [('ui', r'^(soft_tick|interface_tick|swap_tick|type_tick)')],
 'success':    [('chimes', r'^(digital_power_up|interface_confirmation|sparkle|soft_chime|ding)')],
 'confirm':    [('chimes', r'^(interface_confirmation|ding|soft_chime|interface_bong)')],
 'ding':       [('chimes', r'^(ding|soft_chime|sparkle|impact_impact_bell)')],
 'error':      [('alerts', r'')],
 'glitch':     [('scifi', r'(glitch|digital_phase_jump|digital_zap)')],
 'tech':       [('scifi', r'(digital_phaser_up|sci_computer_noise|sci_force_field|digital_pep)')],
 'laser':      [('scifi', r'laser')],
 'coin':       [('foley', r'(chips|coins|chip_lay)')],
 'cash':       [('foley', r'(chips_stack|handle_coins)')],
 'paper':      [('foley', r'(card_slide|card_place|book_flip|card_shove)')],
 'step':       [('foley', r'footstep')],
 'jingle':     [('jingles', r'')],
}
class Pack:
    def __init__(s, seed=None):
        s.man = json.load(open(os.path.join(ROOT, 'manifest.json')))
        s.rng = random.Random(seed); s.used = set(); s.cache = {}
    def files(s, role):
        out = []
        for cat, pat in ROLES[role]:
            out += [f'{cat}/{n}' for n, d in s.man[cat] if re.search(pat, n)]
        return out
    def pick(s, role):
        fs = s.files(role); fresh = [f for f in fs if f not in s.used] or fs
        f = s.rng.choice(fresh); s.used.add(f); return f
    def load(s, rel):
        if rel not in s.cache:
            p = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(ROOT, rel), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True)
            x = np.frombuffer(p.stdout, np.float32).astype(np.float64)
            s.cache[rel] = x / (np.abs(x).max() + 1e-9)
        return s.cache[rel]
    def get(s, role, maxlen=None):
        x = s.load(s.pick(role))
        if maxlen: n = int(maxlen * SR); x = x[:n].copy(); f = min(len(x), int(.03 * SR)); x[-f:] *= np.linspace(1, 0, f)
        return x
