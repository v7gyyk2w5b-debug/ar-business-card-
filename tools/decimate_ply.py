"""
Reduces splat COUNT in a 3D Gaussian Splatting PLY file (not just per-splat
byte size, which gaussian-splats-3d's compressionLevel already handles).

Rather than a pure random subsample, this keeps a set biased toward splats
that actually matter for the rendered image: higher opacity (invisible
splats contribute nothing) and larger scale (bigger splats cover more of
the image, so losing a big one is more visually costly than losing a
tiny one). This is a heuristic, not a proper importance-sampling scheme,
but it's a reasonable first pass for testing mobile performance/quality
tradeoffs.
"""
import struct
import numpy as np
import sys

IN_PATH = "/mnt/user-data/uploads/scene.ply"
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/scene_decimated.ply"
KEEP_FRACTION = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25

with open(IN_PATH, "rb") as f:
    raw = f.read()

header_end = raw.find(b"end_header") + len(b"end_header") + 1  # +1 for newline
header_text = raw[:header_end].decode("ascii")
print("Header fields found:", header_text.count("property"))

vertex_count = int([l for l in header_text.splitlines() if l.startswith("element vertex")][0].split()[-1])
print("Source vertex count:", vertex_count)

# Fields in exact declared order (44 float32 properties per the header we inspected)
field_names = [l.split()[-1] for l in header_text.splitlines() if l.startswith("property")]
n_fields = len(field_names)
row_bytes = n_fields * 4  # all float32

body = raw[header_end:]
expected_bytes = vertex_count * row_bytes
assert len(body) >= expected_bytes, f"body too short: {len(body)} < {expected_bytes}"

arr = np.frombuffer(body, dtype="<f4", count=vertex_count * n_fields).reshape(vertex_count, n_fields)

opacity_idx = field_names.index("opacity")
scale_idx = [field_names.index(f"scale_{i}") for i in range(3)]

# opacity in this format is typically a pre-sigmoid logit; convert for a sane 0-1 weight
opacity_logit = arr[:, opacity_idx]
opacity = 1.0 / (1.0 + np.exp(-opacity_logit))
avg_scale = np.exp(arr[:, scale_idx]).mean(axis=1)  # scale is stored log-space

# importance weight: bigger + more opaque = more visually important
weight = opacity * (avg_scale + 1e-6)
weight = weight / weight.sum()

n_keep = int(vertex_count * KEEP_FRACTION)
rng = np.random.default_rng(42)
keep_idx = rng.choice(vertex_count, size=n_keep, replace=False, p=weight)
keep_idx.sort()

kept = arr[keep_idx]
print(f"Kept {n_keep} / {vertex_count} splats ({KEEP_FRACTION*100:.0f}%)")

new_header = header_text.replace(f"element vertex {vertex_count}", f"element vertex {n_keep}")
with open(OUT_PATH, "wb") as f:
    f.write(new_header.encode("ascii"))
    f.write(kept.astype("<f4").tobytes())

print(f"Wrote {OUT_PATH} ({(header_end + n_keep*row_bytes)/1024/1024:.1f} MB)")
