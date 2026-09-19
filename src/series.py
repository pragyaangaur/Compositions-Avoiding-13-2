"""
Exact computation of A189077: number of compositions of n avoiding the
generalized permutation pattern 13-2 (type (2,1): the "1" and "3" must be
adjacent, the "2" can occur anywhere later).

Route: Heubach, Mansour & Munagi, "Avoiding Permutation Patterns of Type
(2,1) in Compositions", Online J. Anal. Combin. 4 (2009), doi:10.61091/ojac-403.

The paper gives closed-form generating functions for the 12-3 and 23-1
Wilf classes (Theorems 4.1 and 4.3), but for the 13-2 class (our pattern,
Wilf-equivalent to 31-2 by Theorem 3.2) it states explicitly in the
Conclusion: "given explicit generating functions for all but the pattern
13-2, which remains an open question." The only tool it gives for 13-2 is
the *recursive* functional equation in Lemma 4.5, stated there only for the
"full" set A = [d] = {1,...,d}, but whose own right-hand side refers to
generating functions over non-contiguous restricted sets of the form
{1,...,i} u {j,...,d}. So the recursion implicitly requires (and the
paper's proof method, analogous to Theorems 4.1/4.3, licenses) the natural
generalization to an arbitrary ordered set A subset of N. That
generalization is derived and implemented below, in the docstring of coef().

No brute-force enumeration of compositions is performed anywhere in this
file: coefficients are produced by a memoized evaluation, order-by-order in
the power series variable x, of the functional equations for the
generating functions AC^{13-2}_A(v | x) (compositions with parts in A,
avoiding 13-2, whose first part is v), together with AC^{13-2}_A(x) itself.
Because every recursive call multiplies by x^v with v >= 1, the system is
well-founded and can be evaluated exactly with plain Python integers
(no floating point, no truncation error below the requested order).
"""
import sys
import time

sys.setrecursionlimit(1_000_000)


def next_after(A, v):
    """Smallest element of ordered set A (tuple of disjoint (start,end)
    intervals, inclusive, sorted) that is strictly greater than v."""
    for (s, e) in A:
        if s > v:
            return s
        if s <= v <= e:
            if v < e:
                return v + 1
            continue
    return None


def elements_in_range(A, lo, hi):
    """Elements of A that lie in [lo, hi]."""
    res = []
    if lo > hi:
        return res
    for (s, e) in A:
        if e < lo:
            continue
        if s > hi:
            break
        a, b = max(s, lo), min(e, hi)
        if a <= b:
            res.extend(range(a, b + 1))
    return res


def remove_open_interval(A, v, w):
    """Remove the open interval (v, w) from the union-of-intervals A."""
    lo, hi = v + 1, w - 1
    if lo > hi:
        return A
    new = []
    for (s, e) in A:
        if e < lo or s > hi:
            new.append((s, e))
            continue
        if s < lo:
            new.append((s, lo - 1))
        if e > hi:
            new.append((max(s, hi + 1), e))
    return tuple(new)


coef_cache = {}
calls = [0]


def coef(A, v, k):
    """Coefficient of x^k in AC^{13-2}_A(v | x), the generating function
    (with y = 1, i.e. summed over all part-counts m) for compositions with
    parts in A, avoiding 13-2, whose first part is v.

    Derivation of the recursion for general ordered A (generalizing the
    paper's Lemma 4.5, stated there only for A = [d]):

    Let nxt = next_after(A, v) (the immediate successor of v inside A, or
    None if v = max(A)). Decompose by the second part w of the composition
    (or by there being no second part):

        AC_A(v|x) = x^v * ( 1
                             + sum_{w in A, w <= nxt} AC_A(w|x)
                             + sum_{w in A, w >  nxt} AC_{A \\ (v,w)}(w|x) )

    Reasoning: if w <= nxt, then (v, w) contains no element of A at all
    (nxt is v's immediate successor in A), so picking w can never later be
    the "1,3" of an active 13-2 pattern with any third value: no legal
    future part could ever land strictly between v and w. If w > nxt, some
    elements of A lie strictly between v and w; every one of those becomes
    permanently forbidden to all later parts (they would complete the
    pattern 13-2 with the adjacent pair v,w), so the remainder of the
    composition is drawn from A with the open interval (v,w) removed.

    This matches Lemma 4.5 exactly when A = [d] (there nxt(v) = v+1 unless
    v = d, so "w <= nxt" reads "j = 1..i+1" and "w > nxt" reads
    "j = i+2..d", and A \\ (v,w) = {1,...,i} u {j,...,d}).

    Well-foundedness: coef(A,v,k) reduces to coef(*, *, k-v) with v >= 1, so
    recursion strictly decreases the target power-series order; only terms
    with w <= k-v can be nonzero, which is exploited below to avoid scanning
    all of A.
    """
    if k < v:
        return 0
    key = (A, v, k)
    c = coef_cache.get(key)
    if c is not None:
        return c
    calls[0] += 1
    m = k - v
    total = 1 if m == 0 else 0
    if m >= 1:
        nxt = next_after(A, v)
        lo_A = A[0][0]
        if nxt is None:
            w_le = elements_in_range(A, lo_A, m)
            w_gt = []
        else:
            w_le = elements_in_range(A, lo_A, min(nxt, m))
            w_gt = elements_in_range(A, nxt + 1, m)
        for w in w_le:
            total += coef(A, w, m)
        for w in w_gt:
            A2 = remove_open_interval(A, v, w)
            total += coef(A2, w, m)
    coef_cache[key] = total
    return total


def compute_terms(N, time_budget=None):
    """a(0..N) for A189077, using A = [1,N] (parts > n can never occur in a
    composition of n <= N, so this truncation is exact for all n <= N)."""
    A = ((1, N),)
    start = time.time()
    results = []
    for n in range(0, N + 1):
        total = 1 if n == 0 else 0
        for v in range(1, n + 1):
            total += coef(A, v, n)
        results.append(total)
        if time_budget and time.time() - start > time_budget:
            return results, False
    return results, True


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    tb = float(sys.argv[2]) if len(sys.argv) > 2 else None
    t0 = time.time()
    res, complete = compute_terms(N, tb)
    t1 = time.time()
    print(f"# N={N} complete={complete} time={t1-t0:.2f}s calls={calls[0]} "
          f"cache={len(coef_cache)} n_done={len(res)-1}", file=sys.stderr)
    for n, a in enumerate(res):
        print(n, a)
