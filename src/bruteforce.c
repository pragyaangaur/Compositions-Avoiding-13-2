/*
 * Brute-force counter for OEIS A189077: compositions of n avoiding the
 * dashed pattern 13-2.
 *
 * A composition c_1 c_2 ... c_k of n CONTAINS 13-2 if there exist
 * positions i and j with j > i+1 such that c_i < c_j < c_{i+1}.
 * That is: an adjacent ascending pair (c_i, c_{i+1}) with some later
 * (not immediately adjacent) part c_j strictly between the two values.
 * A composition that has no such i,j AVOIDS the pattern, and is counted.
 *
 * Method: every composition of n corresponds to a subset of the n-1 gaps
 * between n unit cells being "cut points" (the classic 2^(n-1) bijection).
 * We enumerate all 2^(n-1) compositions directly (bit i of a mask means
 * "cut after position i+1"), build the part list, and test the pattern
 * directly by brute force over all (i,j) pairs. This is O(k^2) per
 * composition so overall about O(2^n * n^2). It is completely direct and has no
 * cleverness, so it serves as ground truth.
 *
 * Threaded: the 2^(n-1) masks are split into contiguous ranges across
 * up to 5 worker threads, each keeping a local count, summed at the end.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <string.h>

static int N;
static int NUM_THREADS;
static uint64_t thread_counts[5];

typedef struct {
    int thread_id;
    uint64_t lo, hi; /* half-open range of masks [lo, hi) */
} WorkerArg;

/* Test whether the composition given by parts[0..k-1] avoids 13-2.
 * Returns 1 if it avoids (should be counted), 0 if it contains. */
static int avoids(int *parts, int k) {
    for (int i = 0; i + 1 < k; i++) {
        int a = parts[i], b = parts[i + 1];
        if (a < b) {
            /* ascent found: forbid any later part j >= i+2 with a < c_j < b */
            for (int j = i + 2; j < k; j++) {
                if (parts[j] > a && parts[j] < b) {
                    return 0;
                }
            }
        }
    }
    return 1;
}

static void *worker(void *argp) {
    WorkerArg *arg = (WorkerArg *)argp;
    uint64_t local = 0;
    int parts[64]; /* main() rejects N > 63, so at most 63 parts */

    for (uint64_t mask = arg->lo; mask < arg->hi; mask++) {
        /* Build composition of N from mask: bit i (0..N-2) set means
         * there is a cut between unit-cell i+1 and i+2. Parts are runs
         * of consecutive uncut unit cells. */
        int k = 0;
        int run = 1;
        for (int i = 0; i < N - 1; i++) {
            if (mask & (1ULL << i)) {
                parts[k++] = run;
                run = 1;
            } else {
                run++;
            }
        }
        parts[k++] = run;

        if (avoids(parts, k)) {
            local++;
        }
    }
    thread_counts[arg->thread_id] = local;
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s n [threads]\n", argv[0]);
        return 1;
    }
    N = atoi(argv[1]);
    if (N < 0 || N > 63) {
        /* masks are 64-bit and parts[] holds 64 entries */
        fprintf(stderr, "n must be between 0 and 63\n");
        return 1;
    }
    NUM_THREADS = (argc >= 3) ? atoi(argv[2]) : 4;
    if (NUM_THREADS < 1) NUM_THREADS = 1;
    if (NUM_THREADS > 5) NUM_THREADS = 5;

    if (N == 0) {
        /* a(0) = 1: the empty composition, by convention */
        printf("%d %llu\n", N, 1ULL);
        return 0;
    }

    uint64_t total_masks = 1ULL << (N - 1);
    pthread_t threads[5];
    WorkerArg args[5];

    uint64_t chunk = total_masks / NUM_THREADS;
    uint64_t start = 0;
    for (int t = 0; t < NUM_THREADS; t++) {
        args[t].thread_id = t;
        args[t].lo = start;
        args[t].hi = (t == NUM_THREADS - 1) ? total_masks : start + chunk;
        start = args[t].hi;
        pthread_create(&threads[t], NULL, worker, &args[t]);
    }
    uint64_t total = 0;
    for (int t = 0; t < NUM_THREADS; t++) {
        pthread_join(threads[t], NULL);
        total += thread_counts[t];
    }

    printf("%d %llu\n", N, (unsigned long long)total);
    return 0;
}
