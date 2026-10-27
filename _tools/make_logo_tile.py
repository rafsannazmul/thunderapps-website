"""Builds the 3D app-icon tile for the Thunder Apps mark, plus favicons and the iPhone home-screen icon.

    python3 _tools/make_logo_tile.py img/brand/thunder-apps-mark.png img/brand

Needs Pillow and NumPy (pip3 install pillow numpy).
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

MARK = sys.argv[1]
OUT = sys.argv[2]
S = 1024

def squircle_mask(size, n=5.0, ss=4):
    big = size * ss
    y, x = np.mgrid[0:big, 0:big]
    cx = (big - 1) / 2
    u = np.abs((x - cx) / cx); v = np.abs((y - cx) / cx)
    m = ((u ** n + v ** n) <= 1).astype(np.uint8) * 255
    return Image.fromarray(m, 'L').resize((size, size), Image.LANCZOS)

def vgrad(size, top, bottom):
    t = np.linspace(0, 1, size)[:, None]
    arr = np.zeros((size, size, 4), np.uint8)
    for i in range(3):
        arr[..., i] = (top[i] * (1 - t) + bottom[i] * t).astype(np.uint8)
    arr[..., 3] = 255
    return Image.fromarray(arr, 'RGBA')

def build(full_bleed=False):
    mask = Image.new('L', (S, S), 255) if full_bleed else squircle_mask(S)
    tile = vgrad(S, (255, 255, 255), (226, 233, 243))

    # soft top sheen
    sheen = Image.new('L', (S, S), 0)
    ImageDraw.Draw(sheen).ellipse((-S * .25, -S * .75, S * 1.25, S * .42), fill=120)
    sheen = sheen.filter(ImageFilter.GaussianBlur(S * .06))
    tile = Image.composite(Image.new('RGBA', (S, S), (255, 255, 255, 255)), tile, sheen)

    # mark, scaled to fit
    mark = Image.open(MARK).convert('RGBA')
    h = int(S * .74); w = int(mark.width * h / mark.height)
    mark = mark.resize((w, h), Image.LANCZOS)
    ox = (S - w) // 2 - int(S * .01); oy = (S - h) // 2 - int(S * .02)
    alpha = mark.getchannel('A')

    # cast shadow under the mark
    sh = Image.new('L', (S, S), 0); sh.paste(alpha, (ox + int(S * .02), oy + int(S * .045)))
    sh = sh.filter(ImageFilter.GaussianBlur(S * .028)).point(lambda p: int(p * .38))
    tile = Image.composite(Image.new('RGBA', (S, S), (10, 40, 90, 255)), tile, sh)

    # extrusion: stacked dark-blue copies give the mark thickness
    depth = int(S * .022)
    for d in range(depth, 0, -1):
        layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        shade = 50 + int(30 * (1 - d / depth))
        solid = Image.new('RGBA', (w, h), (0, shade, shade + 80, 255))
        layer.paste(solid, (ox + d // 2, oy + d), alpha)
        tile.alpha_composite(layer)
    tile.alpha_composite(mark, (ox, oy))

    if not full_bleed:
        # hairline edge + inner highlight for a raised feel
        edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(5)))
        tile = Image.composite(Image.new('RGBA', (S, S), (170, 182, 200, 255)), tile, edge.point(lambda p: int(p * .55)))
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(tile, (0, 0), mask)
    return out

icon = build()
icon.save(f'{OUT}/thunder-apps-icon-3d.png', optimize=True)
for px in (144, 112):
    icon.resize((px, px), Image.LANCZOS).save(f'{OUT}/thunder-apps-icon-3d-{px}.png', optimize=True)
for px in (32, 48, 192):
    icon.resize((px, px), Image.LANCZOS).save(f'{OUT}/favicon-{px}.png', optimize=True)
full = build(full_bleed=True).convert('RGB')
full.resize((180, 180), Image.LANCZOS).save(f'{OUT}/apple-touch-icon.png', optimize=True)
full.resize((512, 512), Image.LANCZOS).save(f'{OUT}/thunder-apps-icon-512.png', optimize=True)
print('ok')
