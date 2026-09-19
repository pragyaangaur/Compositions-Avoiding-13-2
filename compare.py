#!/usr/bin/env python3
"""Compare the three independent computations of A189077 with each other,
with the 16 terms published in OEIS, and with the b-file."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLISHED = [1, 1, 2, 4, 8, 16, 31, 60, 115, 218, 411, 770, 1434, 2656, 4897, 8991]


def load(name):
    with open(os.path.join(HERE, "data", name)) as f:
        return {int(n): int(v) for n, v in (line.split() for line in f if line.strip())}


brute = load("bruteforce_0_36.txt")
dp = load("dp_0_70.txt")
series = load("series_0_70.txt")
bfile = load("b189077.txt")

ok = True
for name, terms in [("bruteforce", brute), ("dp", dp), ("series", series)]:
    if any(terms[n] != PUBLISHED[n] for n in range(16)):
        print(f"{name}: does not reproduce the published terms")
        ok = False
for n in bfile:
    values = {bfile[n], dp[n], series[n]} | ({brute[n]} if n in brute else set())
    if len(values) != 1:
        print(f"n={n}: disagreement {values}")
        ok = False
print(f"bruteforce n=0..{max(brute)}, dp n=0..{max(dp)}, series n=0..{max(series)}, b-file n=0..{max(bfile)}")
print("all agree" if ok else "MISMATCH")
