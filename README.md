# Compositions Avoiding 13-2

OEIS [A189077](https://oeis.org/A189077) counts the compositions of n that avoid the pattern 13-2. It had 16 terms (n = 0 to 15) for 15 years. This repository computes the terms for n = 0 to 70 in three independent ways, and all three agree.

A composition of n is an ordered list of positive integers that sum to n. It contains the pattern 13-2 when two adjacent parts c_i < c_{i+1} are followed somewhere later by a part c_j with c_i < c_j < c_{i+1}. For example, 1 3 2 contains it, and 1 3 1 2 contains it too. A composition that contains no such triple avoids the pattern.

## The terms

The first new terms are a(16) = 16444, a(17) = 29966, a(18) = 54437, a(19) = 98602 and a(20) = 178127. The full list for n = 0 to 70 is in [data/b189077.txt](data/b189077.txt) in OEIS b-file format. The last term is a(70) = 365109202392731361.

## How the terms were checked

Each program shares no code with the others.

| Program | Method | Range |
| --- | --- | --- |
| [src/bruteforce.c](src/bruteforce.c) | Lists all 2^(n-1) compositions and tests the pattern directly. | n = 0 to 36 |
| [src/dp.py](src/dp.py) | Builds the composition left to right and remembers the remaining sum, the last part, and the set of values that later parts may no longer use. | n = 0 to 70 |
| [src/series.py](src/series.py) | Evaluates the recursive functional equation of Lemma 4.5 in Heubach, Mansour and Munagi (2009), extended from the part set [d] to any set of parts, as an exact power series. | n = 0 to 70 |

All three reproduce the 16 published terms, and they agree on every n where they overlap. [src/check.py](src/check.py) is a fourth, short brute force in Python that checks n = 0 to 24 against the b-file.

The paper states Lemma 4.5 only for the part set [d] = {1, ..., d}. Its right-hand side already uses sets with a gap in the middle, so series.py uses the same recursion for any set of parts. The derivation is in the docstring of `coef()` in series.py, and it reduces to the paper's lemma when the set is [d]. This extension is written here for the computation, and the paper does not state it.

## What this does not claim

The paper says that a closed-form generating function for 13-2 is still an open question. This repository does not answer that question. It only computes more terms.

The dynamic program in dp.py slows down quickly as n grows. It reached n = 109 before it was stopped. The terms past n = 70 are left out because only one program covers them.

## Run it

```
python3 compare.py
python3 src/check.py
python3 src/dp.py 0 40
python3 src/series.py 30
cc -O2 -pthread -o bruteforce src/bruteforce.c && ./bruteforce 25 4
```

`compare.py` checks the saved outputs in [data/](data) against each other and against the published terms. The other commands recompute terms from scratch. The brute force prints one term and takes about 6 minutes at n = 35 on 5 threads.

## Credits

The sequence was created by N. J. A. Sloane in 2011 from S. Heubach, T. Mansour and A. O. Munagi, [Avoiding Permutation Patterns of Type (2,1) in Compositions](https://doi.org/10.61091/ojac-403), Online Journal of Analytic Combinatorics 4 (2009). The recursion in series.py comes from their Lemma 4.5, and the 16 original terms come from their Example 4.6.
