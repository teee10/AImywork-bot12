# 株式会社サード PV 用 BGM を合成して music.wav に書き出す（120BPM / 45秒）
# 映像のシーン切り替え（4s, 7s, 12s, 18s, 24s, 30s, 36s, 38s）にヒットを合わせている
import os
import wave
import numpy as np

SR = 44100
DUR = 45.5
N = int(SR * DUR)
BEAT = 0.5
rs = np.random.RandomState(3)

L = np.zeros(N)
R = np.zeros(N)
REV = np.zeros(N)  # reverb send (mono)


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
    i = int(start * SR)
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


# ---------- instruments ----------
def kick(dec=6.0):
    t = tt(0.6)
    f = 45 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * dec)
    s += rs.randn(len(t)) * np.exp(-t * 250) * 0.25
    return np.tanh(s * 1.8)


def clap():
    t = tt(0.4)
    env = sum(np.exp(-np.maximum(t - d, 0) * 90) * (t >= d) for d in (0, 0.011, 0.023))
    env += np.exp(-t * 14) * 0.35
    return filt(rs.randn(len(t)), 900, 5000) * env


def hat(open_=False):
    t = tt(0.35 if open_ else 0.08)
    return filt(rs.randn(len(t)), 7000) * np.exp(-t * (13 if open_ else 70))


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
    f = 200 * (12 ** p)
    sw = np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 3 * 0.25
    return nz + sw


def whoosh(d=0.9):
    t = tt(d)
    env = np.sin(np.pi * t / d) ** 2
    return filt(rs.randn(len(t)), 400, 4500) * env


def tick():
    t = tt(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200)


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
    sq = np.sign(np.sin(2 * np.pi * mf(m) * t)) * 0.6 + saw(mf(m) * 1.005, t) * 0.4
    return sq * np.exp(-t * 16)


def stab(notes):
    t = tt(0.9)
    s = sum(saw(mf(m + d), t) for m in notes for d in (-0.1, 0.1)) / (2 * len(notes))
    return filt(s, None, 5000) * np.exp(-t * 5)


# ---------- arrangement ----------
PROG = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]  # Am F C G
ROOT = [45, 41, 48, 43]

# pad (dark + bright layers, crossfaded by section)
padD = np.zeros(N)
padB = np.zeros(N)
for b in range(18):  # 0-36s
    c = PROG[b % 4]
    s = chord_saws(c + [c[0] - 12], 2.6)
    i = int(b * 2 * SR)
    j = min(N, i + len(s))
    padD[i:j] += s[: j - i]
padB = filt(padD, None, 3200)
padD = filt(padD, None, 700)
tl = np.arange(N) / SR
lvD = np.interp(tl, [0, 3, 4, 12, 30, 36, 36.01], [0, .55, .6, .5, .35, .5, 0])
lvB = np.interp(tl, [0, 11, 12, 29.9, 30, 35, 36, 36.01], [0, .1, .45, .45, .7, .8, .8, 0])

# sidechain envelope from kicks
kicks = []
for k in range(10, 14):
    kicks.append((k * BEAT, .45))           # 5-7s heartbeat
for k in range(16, 24):
    kicks.append((k * BEAT, .8))            # 8-12 build
for k in range(24, 60):
    kicks.append((k * BEAT, 1.0))           # 12-30 groove
for k in range(68, 72):
    kicks.append((k * BEAT, .85))           # 34-36
for tk in (36.0, 36.5, 37.0, 38.0):
    kicks.append((tk, 1.0))
sc = np.ones(N)
for tk, g in kicks:
    i = int(tk * SR)
    d = tt(0.45)
    j = min(N, i + len(d))
    sc[i:j] = np.minimum(sc[i:j], 1 - 0.75 * g * np.exp(-d[: j - i] * 9))
    put(tk, kick(), 0.9 * g)

pad = padD * lvD + padB * lvB
duck = np.where((tl > 12) & (tl < 36), sc, 1.0)
pad *= duck
put(0, pad, 0.9, -0.15, send=0.35)
put(0, np.roll(pad, int(0.012 * SR)), 0.9, 0.15)

# opening ticks
for k in range(8):
    put(k * BEAT, tick(), 0.18, -0.4 if k % 2 else 0.4, send=0.5)

# risers / impacts / whooshes / crashes
put(1.8, riser(2.2), 0.8, send=0.3)
put(4.0, impact(), 1.0, send=0.6)
put(4.0, crash(), 0.25, send=0.4)
put(9.5, riser(2.5), 0.9, send=0.3)
put(12.0, impact(), 0.9, send=0.5)
put(12.0, crash(), 0.35, send=0.4)
for tw in (17.55, 23.55, 29.55):
    put(tw, whoosh(), 0.35, send=0.3)
    put(tw + 0.45, crash(1.8), 0.22, send=0.3)
put(33.0, riser(3.0), 0.9, send=0.3)
put(37.5, riser(0.5) * 2, 0.8, send=0.3)
put(38.0, impact(6.0), 1.1, send=0.8)
put(38.0, crash(4.0), 0.4, send=0.5)

# hats
for k in range(40, 48):  # 10-12 build: 8ths
    put(k * BEAT, hat(), 0.18 + 0.02 * (k - 40), 0.3)
for k in range(48, 120):  # 12-30 groove: 16ths closed, offbeat open
    t0 = k * BEAT / 2
    if k % 2:
        put(t0, hat(True), 0.22, -0.25)
    else:
        put(t0 + BEAT / 4, hat(), 0.14, 0.35)
    put(t0, hat(), 0.08, 0.35)

# claps (beat 2/4) + rolls
for k in range(24, 60):
    if k % 2 == 1:
        put(k * BEAT, clap(), 0.5, 0.05, send=0.4)
for t0, t1 in ((11.0, 12.0), (35.0, 36.0)):
    tr = t0
    while tr < t1 - 1e-6:
        p = (tr - t0) / (t1 - t0)
        put(tr, clap(), 0.15 + 0.4 * p, send=0.3)
        tr += 0.125 if p < 0.5 else 0.0625

# bass (8ths, sidechained) 12-30 and 34-36
bass = np.zeros(N)
for k in range(48, 120):
    tb = k * BEAT / 2
    if 30 <= tb < 34:
        continue
    root = ROOT[int(tb // 2) % 4]
    t = tt(0.24)
    s = saw(mf(root), t) * 0.7 + np.sin(2 * np.pi * mf(root - 12) * t) * 0.8
    s *= np.minimum(1, t / 0.005) * np.exp(-t * 6)
    i = int(tb * SR)
    bass[i:i + len(s)] += s
for k in range(136, 144):
    tb = k * BEAT / 2
    root = ROOT[int(tb // 2) % 4]
    t = tt(0.24)
    s = saw(mf(root), t) * 0.7 + np.sin(2 * np.pi * mf(root - 12) * t) * 0.8
    s *= np.minimum(1, t / 0.005) * np.exp(-t * 6)
    i = int(tb * SR)
    bass[i:i + len(s)] += s
bass = filt(bass, 30, 900) * sc
put(0, bass, 0.55)

# arpeggio breakdown 30-36 (+ light in 24-30)
for k in range(96, 144):
    ta = k * BEAT / 2
    if ta < 24:
        continue
    c = PROG[int(ta // 2) % 4]
    seq = [c[0] + 12, c[1] + 12, c[2] + 12, c[1] + 24]
    g = 0.10 if ta < 30 else 0.18
    put(ta, filt(pluck(seq[k % 4]), None, 4500), g, -0.5 if k % 2 else 0.5, send=0.45)

# stabs 36 / 36.5 / 37  ->  Am resolve at 38
for ts, c in ((36.0, [53, 57, 60, 65]), (36.5, [55, 59, 62, 67]), (37.0, [52, 56, 59, 64])):
    put(ts, stab(c), 0.55, send=0.5)
    put(ts, crash(0.6), 0.15)
fin = chord_saws([45, 57, 60, 64, 69, 72], 7.0, atk=0.02, rel=6.5)
fin = filt(fin, None, 2600)
put(38.0, fin, 0.9, send=0.6)
t = tt(6.0)
put(38.0, np.sin(2 * np.pi * mf(33) * t) * np.exp(-t * 0.8), 0.5)

# ---------- reverb ----------
irl = tt(3.0)
ir_env = np.exp(-irl / 0.7)
irL = rs.randn(len(irl)) * ir_env
irR = rs.randn(len(irl)) * ir_env
irL = filt(irL, 200, 6000)
irR = filt(irR, 200, 6000)
n2 = 1 << int(np.ceil(np.log2(N + len(irl))))
RV = np.fft.rfft(REV, n2)
wetL = np.fft.irfft(RV * np.fft.rfft(irL, n2), n2)[:N]
wetR = np.fft.irfft(RV * np.fft.rfft(irR, n2), n2)[:N]
wn = max(np.abs(wetL).max(), np.abs(wetR).max()) + 1e-9
L += wetL / wn * 0.35
R += wetR / wn * 0.35

# ---------- master ----------
mix = np.stack([L, R], 1)
mix = filt(mix[:, 0], 25), filt(mix[:, 1], 25)
mix = np.stack(mix, 1)
fade = np.interp(tl, [0, 0.05, 43.5, 45.3], [0, 1, 1, 0])
mix *= fade[:, None]
mix /= np.abs(mix).max() + 1e-9
drive = 1.8
mix = np.tanh(mix * drive) / np.tanh(drive)
mix *= 0.89

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
