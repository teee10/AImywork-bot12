# クロージング代行サービス紹介動画用 BGM（120BPM / 120秒）を合成して music.wav に書き出す
# 各シーンの切り替え（scenes.js の SCENES）にヒットを合わせている
import os
import wave
import numpy as np

SR = 44100
DUR = 120.5
N = int(SR * DUR)
BEAT = 0.5
rs = np.random.RandomState(7)
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


# ---------- timeline ----------
# 0-10 opening
for k in range(8):
    put(k * BEAT, tick(), 0.18, -0.4 if k % 2 else 0.4, send=0.5)
for tp in (4, 5, 6, 7, 8):
    put(tp, low_hit(), 0.8, send=0.5)
    put(tp, stab([57, 60, 63]), 0.18, send=0.6)
kicks(4, 9.5, step=BEAT, g=0.45)
put(7.5, riser(2.5), 0.8, send=0.3)
# 10-18 title
hit(10, 1.1, 0.35)
kicks(10, 13, step=BEAT * 2, g=0.9)
claps(10, 13, half=True)
hit(13, 0.6, 0.25)
kicks(13, 18)
hats(14, 18, 0.7, sixteenth=False)
put(16, riser(2), 0.8, send=0.3)
roll(17, 18)
# 18-30 concept (groove A)
hit(18, 0.8, 0.35)
kicks(18, 30)
hats(18, 30, 0.9)
bass(18, 30, 0.9)
swoosh(23.8)
# 30-48 problems (groove B)
hit(30, 0.7, 0.3)
kicks(30, 48)
hats(30, 48)
claps(30, 48)
bass(30, 48)
for tw in (31.6, 37.07, 42.53):
    swoosh(tw)
put(46, riser(2), 0.6, send=0.3)
# 48-66 menu (+ arp)
swoosh(48)
kicks(48, 66)
hats(48, 66)
claps(48, 66)
bass(48, 66)
arp(48, 64, 0.8)
roll(64, 66, 0.8)
put(63.5, riser(2.5), 0.7, send=0.3)
# 66-86 flow
swoosh(66)
kicks(70, 84)
hats(66, 84, 0.8)
bass(70, 84)
claps(74, 84)
arp(66, 84, 1.0)
put(83, riser(2.8), 0.9, send=0.3)
roll(84, 85.5)
# 86-104 why third (drop)
hit(86, 1.1, 0.4)
kicks(86, 102)
hats(86, 102, 1.1)
claps(86, 102)
bass(86, 102, 1.1)
arp(86, 102, 1.1, octave=24)
for tw in (88.6, 93.73, 98.87):
    swoosh(tw)
kicks(102, 104, step=BEAT / 2, g=0.7)
roll(102, 104)
put(101, riser(3), 0.9, send=0.3)
# 104-112 climax
for ts, c in ((104.0, [53, 57, 60, 65]), (104.5, [55, 59, 62, 67]), (105.0, [57, 60, 64, 69]), (105.5, [52, 56, 59, 64])):
    put(ts, stab(c), 0.6, send=0.5)
    put(ts, KICK, 0.9)
    put(ts, crash(0.6), 0.15)
hit(106, 1.0, 0.4)
kicks(106, 111.5)
hats(108, 111.5, 0.9)
bass(106, 111.5, 1.0)
put(109.5, riser(2.5), 1.0, send=0.3)
roll(110.5, 112)
# 112-120 ending
put(112, impact(6.0), 1.1, send=0.8)
put(112, crash(4.0), 0.4, send=0.5)
fin = filt(chord_saws([45, 57, 60, 64, 69, 72], 8.0, atk=0.02, rel=7.5), None, 2600)
put(112, fin, 0.9, send=0.6)
d = tt(7.0)
put(112, np.sin(2 * np.pi * mf(33) * d) * np.exp(-d * 0.7), 0.5)

# pad (dark/bright layers, level by section)
pad = np.zeros(N)
for b in range(56):  # 0-112s
    c = PROG[b % 4]
    s = chord_saws(c + [c[0] - 12], 2.6)
    i = b * 2 * SR
    j = min(N, i + len(s))
    pad[i:j] += s[: j - i]
padB = filt(pad, None, 3200)
padD = filt(pad, None, 700)
lvD = np.interp(tl, [0, 3, 10, 18, 30, 104, 111.9, 112], [0, .55, .6, .5, .35, .35, .5, 0])
lvB = np.interp(tl, [0, 9.9, 10, 18, 30, 66, 86, 104, 106, 111.9, 112], [0, .05, .45, .4, .4, .45, .5, .5, .8, .8, 0])
padmix = padD * lvD + padB * lvB

# sidechain from kicks
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
mix *= np.interp(tl, [0, 0.05, 118.5, 120.3], [0, 1, 1, 0])[:, None]
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
