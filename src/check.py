#!/usr/bin/env python3
# Brute-force check for OEIS A189077 (compositions of n avoiding 13-2).
# A composition c avoids 13-2 unless some i, j with j > i+1 have
# c[i] < c[j] < c[i+1]. This enumerates every composition directly.

def compositions(n):
    if n == 0:
        yield ()
        return
    for first in range(1, n + 1):
        for rest in compositions(n - first):
            yield (first,) + rest

def avoids_13_2(c):
    return not any(c[i] < c[j] < c[i + 1]
                   for i in range(len(c) - 2) for j in range(i + 2, len(c)))

def a(n):
    return sum(1 for c in compositions(n) if avoids_13_2(c))


computed = [a(n) for n in range(25)]
print(",".join(str(x) for x in computed))
bfile = {int(n): int(v) for n, v in (line.split() for line in open(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "data", "b189077.txt")))}
print("match:", computed == [bfile[n] for n in range(25)])
