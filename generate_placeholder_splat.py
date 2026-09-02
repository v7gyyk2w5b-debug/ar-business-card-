"""
Generates a placeholder .splat file (the antimatter15/gsplat binary format used
by @mkkellogg/GaussianSplats3D) so we can wire up + test the AR pipeline before
we have a real gaussian splat capture.

Each splat record is 32 bytes:
  position   : 3 x float32   (12 bytes)
  scale      : 3 x float32   (12 bytes)
  color      : 4 x uint8 rgba (4 bytes)
  rotation   : 4 x uint8 packed quaternion (4 bytes) -- identity here

Produces a small rainbow-colored sphere of "gaussians" floating above the
tracked image target, purely to prove: image target recognized -> splat
renders anchored in place. Swap this file out for a real capture later.
"""
import struct
import random
import math

OUT_PATH = "assets/placeholder.splat"
NUM_POINTS = 4000
RADIUS = 0.15  # meters-ish, scaled relative to the tracked image size

def hsv_to_rgb(h, s, v):
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i % 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def main():
    records = bytearray()
    for _ in range(NUM_POINTS):
        # random point inside a sphere
        u = random.random()
        v = random.random()
        theta = 2 * math.pi * u
        phi = math.acos(2 * v - 1)
        r = RADIUS * (random.random() ** (1/3))
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta) + RADIUS  # float above the card
        z = r * math.cos(phi)

        # color by height for a simple gradient look
        hue = (y / (2 * RADIUS)) % 1.0
        cr, cg, cb = hsv_to_rgb(hue, 0.7, 1.0)

        scale = 0.004  # small isotropic blobs
        rec = struct.pack(
            "<fff fff BBBB BBBB",
            x, y, z,
            scale, scale, scale,
            cr, cg, cb, 255,
            128, 128, 128, 255,  # identity rotation, packed
        )
        records += rec

    with open(OUT_PATH, "wb") as f:
        f.write(records)

    print(f"Wrote {NUM_POINTS} splats ({len(records)} bytes) to {OUT_PATH}")

if __name__ == "__main__":
    main()
