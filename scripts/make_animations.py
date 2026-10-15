#!/usr/bin/env python3
"""Render the signature's animated GIFs from the source images in assets/src/.

Email clients don't run CSS animation or JavaScript, so motion comes from
animated GIFs. Classic Outlook for Windows shows only the first frame, so the
first frame of every GIF is a finished still.

Outputs (assets/):
  portrait-live.gif   124px  light arc orbiting the portrait ring
  logo-live.gif        60px  NP monogram with a slow light sheen
  rule-live.gif        44px  slate rule with a glint travelling along it
  whatsapp-live.gif    18px  WhatsApp icon with a soft ripple
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets" / "src", ROOT / "assets"

CHARCOAL = np.array([27, 30, 35], float)
TAUPE = np.array([214, 205, 195], float)      # panel B
RING = np.array([205, 195, 185], float)
SLATE = np.array([117, 126, 140], float)
WHITE = np.array([255, 255, 255], float)
GREEN = np.array([31, 138, 91], float)
SS = 4  # supersampling factor


def save_gif(frames, path, durations, loop=0, keys=()):
    """Quantise every frame against one shared palette so nothing flickers, then
    store each later frame as a delta: unchanged pixels become transparent, so a
    small moving highlight costs a few KB per frame instead of a full photo."""
    h = frames[0].height
    picks = frames[:: max(1, len(frames) // 6)][:6]
    sample = Image.new("RGB", (frames[0].width, h * len(picks)))
    for i, f in enumerate(picks):
        sample.paste(f.convert("RGB"), (0, i * h))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pv = np.array(pal.getpalette()[: 255 * 3], float).reshape(-1, 3)
    # Pin exact panel colours so the GIF's background matches the table cell.
    for k in keys:
        pv[np.argmin(((pv - k) ** 2).sum(1))] = k
    pv = np.unique(pv.round(), axis=0)               # no duplicate entries
    lut = np.zeros((256, 3), np.uint8); lut[: len(pv)] = pv
    palette = lut.flatten().tolist()

    def to_index(f):                                  # exact nearest colour
        rgb = np.asarray(f.convert("RGB")).reshape(-1, 3)
        cols, inv = np.unique(rgb, axis=0, return_inverse=True)
        d = ((cols[:, None, :].astype(float) - pv[None]) ** 2).sum(-1)
        return d.argmin(1)[inv.ravel()].reshape(f.height, f.width).astype(np.uint8)

    q = [to_index(f) for f in frames]
    same = lambda a, b: np.array_equal(lut[a], lut[b])
    durs = list(durations) if isinstance(durations, (list, tuple)) else [durations] * len(q)
    # Merge frames identical to the previous one (Pillow would drop them anyway).
    keep_q, keep_d = [q[0]], [durs[0]]
    for cur, d in zip(q[1:], durs[1:]):
        if same(cur, keep_q[-1]):
            keep_d[-1] += d
        else:
            keep_q.append(cur); keep_d.append(d)
    q, durations = keep_q, keep_d
    TR = 255
    out = []
    for i, cur in enumerate(q):
        fr = cur.copy()
        if i:
            fr[(lut[cur] == lut[q[i - 1]]).all(-1)] = TR
        im = Image.fromarray(fr.astype(np.uint8), "P")
        im.putpalette(palette)
        out.append(im)
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=loop,
                optimize=False, disposal=1, transparency=TR)
    # verify: every decoded frame must equal its quantised source frame
    chk = Image.open(path)
    for i, cur in enumerate(q):
        chk.seek(i)
        if not np.array_equal(np.asarray(chk.convert("RGB")), lut[cur]):
            raise SystemExit(f"{path.name}: frame {i} does not decode as rendered")
    print(f"{path.name}: {len(q)} frames, {path.stat().st_size/1024:.1f} KB")


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- portrait
def portrait():
    D = 248                     # 2x of 124px display
    N = D * SS
    im = Image.open(SRC / "portrait-original.jpg").convert("RGB")
    cx, cy, s = 655, 460, 720
    photo = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).resize((N, N), Image.LANCZOS)
    rw, gap = 4 * SS, 7 * SS
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).ellipse((rw + gap, rw + gap, N - 1 - rw - gap, N - 1 - rw - gap), fill=255)

    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N / 2, yy - N / 2)
    ang = (np.degrees(np.arctan2(yy - N / 2, xx - N / 2)) + 360) % 360
    ring = np.clip(1 - np.abs(r - (N / 2 - rw / 2 - 1)) / (rw / 2 + 1), 0, 1)  # anti-aliased band

    base = Image.new("RGB", (N, N), tuple(CHARCOAL.astype(int)))
    base.paste(photo, (0, 0), mask)
    base_np = np.asarray(base, float)

    photo_m = np.asarray(mask, float)[..., None] / 255
    frames = []
    n = 30
    for i in range(n):
        head = (300 + i * 360 / n) % 360            # starts top-right, clockwise
        behind = (head - ang) % 360                 # degrees behind the head
        tail = np.clip(1 - behind / 140, 0, 1) ** 1.8
        lit = RING + (WHITE - RING) * tail[..., None]
        alpha = ring * (0.5 + 0.5 * tail)
        out = base_np * (1 - alpha[..., None]) + lit * alpha[..., None]
        # soft glow that spills into the dark gap, never over the photo
        g = Image.fromarray((ring * tail * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4 * SS))
        glow = np.asarray(g, float)[..., None] / 255 * 1.6 * (1 - photo_m)
        out = out + (WHITE - out) * np.clip(glow, 0, 0.7)
        frames.append(Image.fromarray(out.astype(np.uint8)).resize((D, D), Image.LANCZOS))
    save_gif(frames, OUT / "portrait-live.gif", 110, keys=[CHARCOAL])


# ---------------------------------------------------------------- logo
def logo():
    D = 120                     # 2x of 60px display
    src = np.asarray(Image.open(SRC / "np-logo-original.png").convert("RGB"), float)
    lum = src @ [0.299, 0.587, 0.114]
    a = np.clip((lum - 40) / 75, 0, 1)
    white = np.clip((lum - 150) / 80, 0, 1)[..., None]
    col = SLATE * (1 - white) + WHITE * white
    bb = (20, 15, 606, 592)
    a, col = a[bb[1]:bb[3], bb[0]:bb[2]], col[bb[1]:bb[3], bb[0]:bb[2]]
    h, w = a.shape
    S = max(h, w) + 40          # small margin
    A = np.zeros((S, S)); C = np.zeros((S, S, 3))
    oy, ox = (S - h) // 2, (S - w) // 2
    A[oy:oy + h, ox:ox + w] = a; C[oy:oy + h, ox:ox + w] = col
    yy, xx = np.mgrid[0:S, 0:S] / S

    frames, durs = [], []
    n = 22
    for i in range(n + 1):
        t = i / n                                  # sheen position 0..1
        pos = -0.35 + 1.7 * smooth(t)
        band = np.exp(-(((xx + yy) / 2 - pos) / 0.07) ** 2)
        lit = C + (WHITE - C) * band[..., None] * 0.85
        out = CHARCOAL * (1 - A[..., None]) + lit * A[..., None]
        frames.append(Image.fromarray(out.astype(np.uint8)).resize((D, D), Image.LANCZOS))
        durs.append(3200 if i == 0 else 55)
    durs[-1] = 1800
    save_gif(frames, OUT / "logo-live.gif", durs, keys=[CHARCOAL])


# ---------------------------------------------------------------- rule
def rule():
    W, H = 88, 2                # 2x of 44x1 display
    frames, durs = [], []
    n = 18
    xs = np.arange(W)
    for i in range(n + 1):
        p = -20 + (W + 40) * smooth(i / n)
        g = np.exp(-((xs - p) / 9) ** 2)
        row = SLATE + (WHITE - SLATE) * g[:, None] * 0.9
        arr = np.repeat(row[None], H, 0)
        frames.append(Image.fromarray(arr.astype(np.uint8)))
        durs.append(2600 if i == 0 else 45)
    save_gif(frames, OUT / "rule-live.gif", durs, keys=[SLATE])


# ---------------------------------------------------------------- whatsapp
def whatsapp():
    D = 72                      # 4x of 18px display (matches the static icons)
    icon = Image.open(OUT / "icon-whatsapp.png").convert("RGBA").resize((D * SS, D * SS), Image.LANCZOS)
    ia = np.asarray(icon, float)
    N = D * SS
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N / 2, yy - N / 2) / (N / 2)
    frames, durs = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        rr = 0.25 + 0.75 * t
        ripple = np.exp(-((r - rr) / 0.07) ** 2) * (1 - t) * 0.55
        rgb = ia[..., :3] + (WHITE - ia[..., :3]) * ripple[..., None] * (ia[..., :3].mean(-1, keepdims=True) < 200)
        al = ia[..., 3:4] / 255
        out = TAUPE * (1 - al) + rgb * al          # matte onto the taupe panel
        frames.append(Image.fromarray(out.astype(np.uint8)).resize((D, D), Image.LANCZOS))
        durs.append(2400 if i == 0 else 60)
    save_gif(frames, OUT / "whatsapp-live.gif", durs, keys=[TAUPE])


if __name__ == "__main__":
    portrait(); logo(); rule(); whatsapp()
