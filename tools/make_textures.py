"""Generate tileable material textures for the new-build cabins.

Colors are sampled from the manufacturers' product photos (regions picked
by hand); the plank/tile patterns are procedural, so no photo pixels are
redistributed. Each texture tiles 2x2 meters; the viewer uses repeat 0.5
with meter-space UVs.

Writes web/tex/<name>.png (256x256).
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'web' / 'tex'
OUT.mkdir(parents=True, exist_ok=True)
SCRATCH = Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp' / 'claude' / \
    'C--Users-foeijord-Code-hytte' / 'df508fcc-9c6d-4069-b80b-9d512890f5b8' / 'scratchpad'

SIZE = 256                 # px per 2 m tile
rng = np.random.default_rng(437109)


def sample(img_name, box, fallback):
    """Median color of a crop box (fractions of width/height)."""
    p = SCRATCH / img_name
    if not p.exists():
        return np.array(fallback, dtype=float)
    im = np.asarray(Image.open(p).convert('RGB'), dtype=float)
    h, w = im.shape[:2]
    x0, y0, x1, y1 = box
    crop = im[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    return np.median(crop.reshape(-1, 3), axis=0)


def planks(base, horizontal=True, plank_m=0.20, gap=0.012, jitter=0.06):
    """Tileable cladding: parallel planks with tone jitter and gap lines."""
    n_planks = max(1, round(2.0 / plank_m))
    px_per = SIZE // n_planks
    img = np.zeros((SIZE, SIZE, 3))
    grain = rng.normal(0, 4, (SIZE, SIZE, 1)).cumsum(axis=1)
    grain -= grain.mean(axis=1, keepdims=True)
    for i in range(n_planks):
        tone = 1 + rng.normal(0, jitter)
        img[i * px_per:(i + 1) * px_per, :] = np.clip(base * tone, 0, 255)
    img += np.clip(grain, -10, 10)
    gap_px = max(1, int(gap / 2.0 * SIZE))
    for i in range(n_planks):
        img[i * px_per:i * px_per + gap_px, :] *= 0.55
    if not horizontal:
        img = img.transpose(1, 0, 2)
    return np.clip(img, 0, 255).astype(np.uint8)


def tiles(base, row_m=0.35, col_m=0.30):
    """Tileable roof: staggered tile rows with edge shadows."""
    img = np.tile(base, (SIZE, SIZE, 1)).astype(float)
    img += rng.normal(0, 5, (SIZE, SIZE, 1))
    rows = max(1, round(2.0 / row_m))
    rpx = SIZE // rows
    cols = max(1, round(2.0 / col_m))
    cpx = SIZE // cols
    for r in range(rows):
        y = r * rpx
        img[y:y + max(1, rpx // 7), :] *= 0.6            # row shadow
        off = (r % 2) * cpx // 2
        for c in range(cols + 1):
            x = (c * cpx + off) % SIZE
            img[y:y + rpx, x:x + 1] *= 0.75              # tile joints
    return np.clip(img, 0, 255).astype(np.uint8)


def seams(base, seam_m=0.5):
    """Standing-seam / flat roof: vertical seams, slight sheen bands."""
    img = np.tile(base, (SIZE, SIZE, 1)).astype(float)
    img += rng.normal(0, 3, (SIZE, 1, 1))
    n = max(1, round(2.0 / seam_m))
    spx = SIZE // n
    for c in range(n):
        x = c * spx
        img[:, x:x + 2] *= 1.25
        img[:, x + 2:x + 3] *= 0.7
    return np.clip(img, 0, 255).astype(np.uint8)


def save(name, arr):
    Image.fromarray(arr).save(OUT / f'{name}.png', optimize=True)
    print(f'{name}: rgb {arr.reshape(-1,3).mean(axis=0).astype(int)}')


# palettes: matched by eye against the product photos (auto-crops hit
# shadows/backgrounds too easily); spang_wall keeps its good sampled value
falstad_wall = np.array((198, 175, 140), dtype=float)     # pale wood (render)
falstad_roof = np.array((45, 44, 46), dtype=float)        # black tile
frem_wall = np.array((224, 219, 210), dtype=float)        # white cladding
frem_roof = np.array((62, 66, 72), dtype=float)           # dark gray tile
spang_wall = sample('spangereid_ext.jpg', (0.12, 0.62, 0.30, 0.80), (185, 168, 135))
spang_roof = np.array((45, 45, 48), dtype=float)          # dark flat roof
furu_wall = np.array((110, 82, 58), dtype=float)          # familiehytta brown stain
furu_roof = np.array((70, 66, 62), dtype=float)

save('wall_frem', planks(frem_wall))                      # Frem 80 + 95
save('roof_frem', tiles(frem_roof))
save('wall_furu', planks(furu_wall))                      # Furutangen 75
save('roof_furu', tiles(furu_roof))
save('wall_falstad', planks(falstad_wall))                # Falstad
save('roof_falstad', tiles(falstad_roof))
save('wall_spang', planks(spang_wall, plank_m=0.15))      # Spangereid funkis
save('roof_spang', seams(spang_roof))
print('done ->', OUT)
