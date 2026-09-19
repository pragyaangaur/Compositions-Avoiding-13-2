#!/usr/bin/env python3
"""
Exact DP for OEIS A189077: compositions of n avoiding the dashed pattern
13-2 (contains 13-2 if c_i < c_j < c_{i+1} for some j > i+1; avoids it
otherwise).

State and why it is correct
----------------------------
Build the composition left to right, one part at a time. To know which
values are legal for the NEXT part, we only need three facts about what
has been placed so far:

  R    - the remaining sum still to be distributed among the parts not
         yet placed.
  L    - the value of the last part placed (or "no part yet" at the
         very start).
  mask - which values are now forbidden for every future part, as a
         bitmask (bit v of mask is 1 iff the integer v may never be
         used again).

Why "forbidden values" is the right thing to track: whenever we place a
part v right after a part L with L < v, that is an ascent. By the
pattern's definition (c_i < c_j < c_{i+1} for j > i+1), no part
placed after v (including the one right after it) may take a value strictly between
L and v. So the moment an ascent (L, v) happens we mark every integer in
the open interval (L, v) as forbidden from then on. If v <= L there is
no ascent and nothing new gets forbidden.

Forbidden values only ever get ADDED, never removed, so mask grows
monotonically as the composition is built. We store it as a plain
integer bitmask (bit i set = value i is forbidden), which makes both
operations O(1) machine words:

  - marking the open interval (L, v) forbidden is one OR with a
    precomputed range-mask,
  - testing "is v forbidden" is one bit test,
  - dropping information about values that can no longer matter (any
    value bigger than the new remaining sum can never be chosen again,
    since a single part cannot exceed what's left) is one AND with a
    low-bits mask.

That last point is what keeps the memoized state space small: every
time R shrinks, mask is clipped down to bits 0..R, so the key shrinks
as the composition nears completion instead of growing without bound.

The recursion is:

  solve(R, L, mask):
      if R == 0: return 1                       # composition complete
      total = 0
      for v in 1..R with bit v of mask == 0:     # v is not forbidden
          m = mask
          if L is not START and L < v:
              m |= range_mask(L, v)              # forbid (L, v)
          m &= low_bits(R - v)                   # clip to what can matter
          total += solve(R - v, v, m)
      return total

  a(n) = solve(n, START, 0)

This is a direct translation of the pattern's definition. It uses no
generating function and no outside formula. It matches the independent
brute-force enumerator (bruteforce.c) on every n where both were run
(see compare.py).
"""
import sys
from functools import lru_cache

sys.setrecursionlimit(1_000_000)

START = -1  # sentinel: "no part has been placed yet"


def range_mask(lo, hi):
    """Bitmask with bits lo+1 .. hi-1 set (the open interval (lo, hi)).
    Empty (0) if hi <= lo + 1, i.e. no integer lies strictly between."""
    if hi <= lo + 1:
        return 0
    return ((1 << hi) - 1) & ~((1 << (lo + 1)) - 1)


def low_bits(r):
    """Bitmask with bits 0..r set, used to clip away information about
    values that can never be chosen again (they exceed the remaining sum)."""
    return (1 << (r + 1)) - 1


@lru_cache(maxsize=None)
def solve(R, L, mask):
    if R == 0:
        return 1
    total = 0
    for v in range(1, R + 1):
        if (mask >> v) & 1:
            continue  # v is forbidden
        m = mask
        if L != START and L < v:
            m |= range_mask(L, v)
        m &= low_bits(R - v)
        total += solve(R - v, v, m)
    return total


def a(n):
    if n == 0:
        return 1
    return solve(n, START, 0)


if __name__ == "__main__":
    import time

    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    for n in range(lo, hi + 1):
        t0 = time.time()
        val = a(n)
        t1 = time.time()
        print(f"{n} {val}", flush=True)
        print(f"# n={n} time={t1 - t0:.3f}s cache={solve.cache_info()}", file=sys.stderr, flush=True)
