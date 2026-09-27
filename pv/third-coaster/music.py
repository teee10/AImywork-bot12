# ジェットコースター版PV用 BGM（120BPM / 72秒）を合成して music.wav に書き出す
# speed.json（render.cjs --speed）の速度に合わせて、チェーンの音・風切り音・走行音を重ねる
import os
import wave
import numpy as np

SR = 44100
DUR = 72.5
N = int(SR * DUR)
BEAT = 0.5
rs = np.random.RandomState(11)
L = np.zeros(N)
R = np.zeros(N)
REV = np.zeros(N)
tl = np.arange(N) / SR


def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def filt(x, lo=None, hi=None):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g /= np.sqrt(1 + (f / hi) ** 4)
    if lo:
        g /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, n)


def put(start, sig, gain=1.0, pan=0.0, send=0.0):
    i = int(round(start * SR))
    if i >= N:
        return
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    a = (pan + 1) * np.pi / 4
    L[i:j] += s * np.cos(a) * 1.414
    R[i:j] += s * np.sin(a) * 1.414
    if send:
        REV[i:j] += s * send


def saw(f, t, ph=0.0):
    return 2 * ((f * t + ph) % 1) - 1


# ---------- instruments (pre-rendered one-shots) ----------
def _kick(dec=6.0):
    t = tt(0.6)
    f = 45 + 120 * np.exp(-t * 32)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec)
    s += rs.randn(len(t)) * np.exp(-t * 250) * 0.25
    return np.tanh(s * 1.8)


def _clap():
    t = tt(0.4)
    env = sum(np.exp(-np.maximum(t - d, 0) * 90) * (t >= d) for d in (0, 0.011, 0.023))
    env += np.exp(-t * 14) * 0.35
    return filt(rs.randn(len(t)), 900, 5000) * env


def _hat(open_=False):
    t = tt(0.35 if open_ else 0.08)
    return filt(rs.randn(len(t)), 7000) * np.exp(-t * (13 if open_ else 70))


KICK, CLAP, HAT, OHAT = _kick(), _clap(), _hat(), _hat(True)


def crash(d=2.5):
    t = tt(d)
    return filt(rs.randn(len(t)), 4000) * np.exp(-t * 1.8)


def impact(d=4.0):
    t = tt(d)
    f = 30 + 60 * np.exp(-t * 3)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1)
    nz = filt(rs.randn(len(t)), None, 2500) * np.exp(-t * 5) * 0.6
    return np.tanh((boom + nz) * 1.5)


def riser(d):
    t = tt(d)
    p = t / d
    nz = filt(rs.randn(len(t)), 1500) * p ** 2.5 * 0.5
    sw = np.sin(2 * np.pi * np.cumsum(200 * (12 ** p)) / SR) * p ** 3 * 0.25
    return nz + sw


def whoosh(d=0.9):
    t = tt(d)
    return filt(rs.randn(len(t)), 400, 4500) * np.sin(np.pi * t / d) ** 2


def tick():
    t = tt(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200)


def low_hit():
    t = tt(1.2)
    f = 40 + 40 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)
    s += filt(rs.randn(len(t)), 200, 1800) * np.exp(-t * 12) * 0.5
    return np.tanh(s * 2)


def chord_saws(notes, d, det=0.12, atk=0.25, rel=0.6):
    t = tt(d)
    s = np.zeros(len(t))
    for m in notes:
        for k, dt in enumerate((-det, 0.0, det)):
            s += saw(mf(m + dt), t, ph=k * 0.31)
    env = np.minimum(1, t / atk) * np.minimum(1, np.maximum(0, (d - t) / rel))
    return s * env / (3 * len(notes))


def pluck(m, d=0.25):
    t = tt(d)
    s = np.sign(np.sin(2 * np.pi * mf(m) * t)) * 0.6 + saw(mf(m) * 1.005, t) * 0.4
    return filt(s * np.exp(-t * 16), None, 4500)


def stab(notes):
    t = tt(0.9)
    s = sum(saw(mf(m + d), t) for m in notes for d in (-0.1, 0.1)) / (2 * len(notes))
    return filt(s, None, 5000) * np.exp(-t * 5)


PROG = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]  # Am F C G
ROOT = [45, 41, 48, 43]


def chord_at(t):
    return PROG[int(t // 2) % 4]


# ---------- arrangement helpers ----------
kick_times = []


def kicks(t0, t1, step=BEAT, g=1.0):
    t = t0
    while t < t1 - 1e-6:
        kick_times.append((t, g))
        put(t, KICK, 0.9 * g)
        t += step


def hats(t0, t1, g=1.0, sixteenth=True):
    k = 0
    t = t0
    while t < t1 - 1e-6:
        if k % 2 == 1:
            put(t, OHAT, 0.2 * g, -0.25)
        elif sixteenth:
            put(t + BEAT / 4, HAT, 0.13 * g, 0.35)
        put(t, HAT, 0.08 * g, 0.35)
        t += BEAT / 2
        k += 1


def claps(t0, t1, g=1.0, half=False):
    t = t0 + (BEAT * 2 if half else BEAT)
    while t < t1 - 1e-6:
        put(t, CLAP, 0.5 * g, 0.05, send=0.4)
        t += BEAT * (4 if half else 2)


def roll(t0, t1, g=1.0):
    t = t0
    while t < t1 - 1e-6:
        p = (t - t0) / (t1 - t0)
        put(t, CLAP, (0.12 + 0.4 * p) * g, send=0.3)
        t += 0.125 if p < 0.5 else 0.0625


BASS = np.zeros(N)


def bass(t0, t1, g=1.0):
    t = t0
    while t < t1 - 1e-6:
        root = ROOT[int(t // 2) % 4]
        d = tt(0.24)
        s = saw(mf(root), d) * 0.7 + np.sin(2 * np.pi * mf(root - 12) * d) * 0.8
        s *= np.minimum(1, d / 0.005) * np.exp(-d * 6) * g
        i = int(round(t * SR))
        j = min(N, i + len(s))
        BASS[i:j] += s[: j - i]
        t += BEAT / 2


def arp(t0, t1, g=1.0, octave=12):
    k = 0
    t = t0
    while t < t1 - 1e-6:
        c = chord_at(t)
        seq = [c[0], c[1], c[2], c[1] + 12]
        put(t, pluck(seq[k % 4] + octave), 0.15 * g, -0.5 if k % 2 else 0.5, send=0.45)
        t += BEAT / 2
        k += 1


def hit(t, big=1.0, crash_g=0.3):
    put(t, impact(), 0.9 * big, send=0.5)
    put(t, crash(), crash_g, send=0.4)


def swoosh(t):
    put(t - 0.45, whoosh(), 0.35, send=0.3)
    put(t, crash(1.8), 0.2, send=0.3)


# ---------- ride SFX (speed-driven) ----------
import json
sp = np.array(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speed.json'))))
v = np.interp(tl, np.arange(len(sp)) / 30, sp)
# リフトのチェーン音（一定距離ごとにカチッ）
dist = np.cumsum(v) / SR
clk = np.where(np.diff(np.floor(dist / 1.4), prepend=0) > 0)[0]
for i in clk:
    tc = i / SR
    if tc > 7.9:
        break
    d = tt(0.05)
    s = filt(rs.randn(len(d)), 1500, 6000) * np.exp(-d * 120) + np.sin(2 * np.pi * 900 * d) * np.exp(-d * 80) * .5
    put(tc, s, 0.35, 0.1 * np.sin(tc * 3), send=0.2)
# 風切り音と走行音（速度に比例）
wind = filt(rs.randn(N), 250, 3500)
wlev = np.clip((v - 8) / 90, 0, 1.3) ** 2 * 0.22
wlev *= np.interp(tl, [0, 62.3, 64, 72.5], [1, 1, .35, .2])
put(0, wind * wlev, 1.0, -0.2)
put(0, np.roll(wind, 3000) * wlev, 1.0, 0.2)
rumble = filt(rs.randn(N), 30, 160) * np.clip(v / 80, 0, 1.2) * 0.35 * (tl < 62.3)
put(0, rumble, 1.0)

# ---------- timeline ----------
# 0-8 リフトアップ（静かな緊張）
put(4.0, riser(3.8), 0.7, send=0.3)
for k in range(8, 15):
    put(k * BEAT, low_hit(), 0.35 + 0.05 * (k - 8), send=0.3)
# 8 ドロップ
hit(8.0, 1.2, 0.45)
kicks(8, 16)
hats(8, 16, 0.8, sixteenth=False)
bass(8, 16)
claps(8, 16)
# 16-26 都庁らせん
kicks(16, 26)
hats(16, 26)
claps(16, 26)
bass(16, 26)
arp(16, 24, 0.8)
roll(25, 26, 0.9)
# ゲート（26 / 36 / 46）
for tg in (26.0, 36.0, 46.0):
    put(tg - 0.6, whoosh(0.7), 0.5, send=0.3)
    hit(tg, 0.7, 0.35)
kicks(26, 56)
hats(26, 56, 1.0)
claps(26, 56)
bass(26, 56, 1.05)
arp(26, 36, 0.9)
arp(36, 46, 1.0, octave=24)
arp(46, 56, 1.1)
for ts in (47.0, 49.0, 51.0, 53.0):
    put(ts, stab(chord_at(ts) + [chord_at(ts)[0] + 12]), 0.3, send=0.4)
# 56-60 上昇ビルド
kicks(56, 58, g=.8)
kicks(58, 59, step=BEAT / 2, g=.8)
kicks(59, 60, step=BEAT / 4, g=.7)
roll(58, 60)
put(56.5, riser(3.5), 1.0, send=0.3)
# 60-62 連打 → 62 発射
for ts, c in ((60.0, [53, 57, 60, 65]), (60.5, [55, 59, 62, 67]), (61.0, [57, 60, 64, 69]), (61.5, [52, 56, 59, 64])):
    put(ts, stab(c), 0.6, send=0.5)
    put(ts, KICK, 0.9)
    put(ts, crash(0.6), 0.15)
put(62.0, impact(6.0), 1.2, send=0.8)
put(62.0, crash(4.0), 0.45, send=0.5)
fin = filt(chord_saws([45, 57, 60, 64, 69, 72], 10.0, atk=0.02, rel=9.5), None, 2600)
put(62.0, fin, 0.9, send=0.6)
d = tt(8.0)
put(62.0, np.sin(2 * np.pi * mf(33) * d) * np.exp(-d * 0.6), 0.5)

# pad
pad = np.zeros(N)
for b in range(31):  # 0-62s
    c = PROG[b % 4]
    s = chord_saws(c + [c[0] - 12], 2.6)
    i = b * 2 * SR
    j = min(N, i + len(s))
    pad[i:j] += s[: j - i]
padB = filt(pad, None, 3200)
padD = filt(pad, None, 700)
lvD = np.interp(tl, [0, 3, 8, 16, 61.9, 62], [.2, .55, .6, .35, .35, 0])
lvB = np.interp(tl, [0, 7.9, 8, 26, 56, 61.9, 62], [0, .05, .4, .45, .55, .6, 0])
padmix = padD * lvD + padB * lvB
sc = np.ones(N)
dd = tt(0.45)
for tk, g in kick_times:
    i = int(round(tk * SR))
    j = min(N, i + len(dd))
    sc[i:j] = np.minimum(sc[i:j], 1 - 0.75 * g * np.exp(-dd[: j - i] * 9))
padmix *= sc
put(0, padmix, 0.9, -0.15, send=0.35)
put(0, np.roll(padmix, int(0.012 * SR)), 0.9, 0.15)
put(0, filt(BASS, 30, 900) * sc, 0.55)

# reverb
irl = tt(3.0)
env = np.exp(-irl / 0.7)
irL = filt(rs.randn(len(irl)) * env, 200, 6000)
irR = filt(rs.randn(len(irl)) * env, 200, 6000)
n2 = 1 << int(np.ceil(np.log2(N + len(irl))))
RV = np.fft.rfft(REV, n2)
wetL = np.fft.irfft(RV * np.fft.rfft(irL, n2), n2)[:N]
wetR = np.fft.irfft(RV * np.fft.rfft(irR, n2), n2)[:N]
wn = max(np.abs(wetL).max(), np.abs(wetR).max()) + 1e-9
L += wetL / wn * 0.35
R += wetR / wn * 0.35

# master
mix = np.stack([filt(L, 25), filt(R, 25)], 1)
mix *= np.interp(tl, [0, 0.05, 70.5, 72.3], [0, 1, 1, 0])[:, None]
mix /= np.abs(mix).max() + 1e-9
drive = 1.8
mix = np.tanh(mix * drive) / np.tanh(drive) * 0.89

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
