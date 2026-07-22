"""Crop real facade bands from the manufacturers' elevation drawings and
save them as wall textures (web/tex/fac_*.jpg). Used for the Drommehytten
designs where clean 4-view elevation sheets are published; crops are
applied per wall face (stretched 0..1), so windows and doors appear at
their true positions.

Sources (downloaded to the session scratchpad):
  falstad2.jpg       Falstad elevation sheet (2x2)
  spangereid_ext.jpg Spangereid elevation sheet (2x2)
"""
import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'web' / 'tex'
OUT.mkdir(parents=True, exist_ok=True)
SCRATCH = Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp' / 'claude' / \
    'C--Users-foeijord-Code-hytte' / 'df508fcc-9c6d-4069-b80b-9d512890f5b8' / 'scratchpad'

# (source, quadrant (col,row), crop box in quadrant fractions, out name)
CROPS = [
    ('falstad2.jpg', (0, 0), (0.075, 0.580, 0.930, 0.930), 'fac_falstad_sea'),
    ('falstad2.jpg', (0, 0), (0.100, 0.060, 0.910, 0.270), 'fac_falstad_cler'),
    ('falstad2.jpg', (0, 1), (0.078, 0.520, 0.930, 0.900), 'fac_falstad_road'),
    ('spangereid_ext.jpg', (0, 0), (0.115, 0.555, 0.845, 0.945), 'fac_spang_sea'),
    ('spangereid_ext.jpg', (0, 0), (0.115, 0.140, 0.845, 0.530), 'fac_spang_upper'),
    ('spangereid_ext.jpg', (0, 1), (0.160, 0.320, 0.800, 0.940), 'fac_spang_road'),
]

for src, (qc, qr), (x0, y0, x1, y1), name in CROPS:
    im = Image.open(SCRATCH / src)
    w, h = im.size
    q = im.crop((qc * w // 2, qr * h // 2, (qc + 1) * w // 2, (qr + 1) * h // 2))
    qw, qh = q.size
    band = q.crop((int(x0 * qw), int(y0 * qh), int(x1 * qw), int(y1 * qh)))
    band = band.resize((band.width * 3, band.height * 3), Image.LANCZOS)
    band.save(OUT / f'{name}.jpg', quality=88)
    print(f'{name}: {band.size}')
print('done ->', OUT)
