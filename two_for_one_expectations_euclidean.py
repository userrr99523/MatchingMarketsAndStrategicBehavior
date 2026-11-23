import time
import csv

## Two for One Code

import itertools
import copy

def gale_shapley(mpref, wpref, strategic_woman=0):
    n = len(mpref)
    curr_match_count = 0
    last_rejected_by_rank_what = [0 for i in range(n)]
    men_matchings = [0 for i in range(n)]
    women_matchings = [0 for i in range(n)]
    proposals_to_strategic_woman = set()    # Only used if strategic_woman != 0

    # continue until all matches made
    while curr_match_count < n:
        for man in range(n):
            # if man is single
            if men_matchings[man] == 0:
                # get first non-rejecting woman from man's preference list
                woman = mpref[man][last_rejected_by_rank_what[man]] - 1
                if woman + 1 == strategic_woman:
                    proposals_to_strategic_woman.add(man + 1)

                # both man and woman are single
                if women_matchings[woman] == 0:
                    # create match (man, woman)
                    men_matchings[man] = woman + 1
                    women_matchings[woman] = man + 1
                    curr_match_count += 1

                # woman is with someone
                else:
                    # find ranks of curr_partner and man given woman's preference list
                    curr_partner = women_matchings[woman]
                    curr_partner_rank = wpref[woman].index(curr_partner)
                    man_rank = wpref[woman].index(man + 1)

                    # woman prefers curr_partner over man
                    if curr_partner_rank < man_rank:
                        last_rejected_by_rank_what[man] = mpref[man].index(woman + 1) + 1

                    # woman prefers man over curr_partner
                    else:
                        men_matchings[curr_partner - 1] = 0
                        last_rejected_by_rank_what[curr_partner - 1] = mpref[curr_partner - 1].index(woman + 1) + 1
                        men_matchings[man] = woman + 1
                        women_matchings[woman] = man + 1

    if strategic_woman != 0:
        return men_matchings, proposals_to_strategic_woman
    else:
        return men_matchings

def generate_sw_manipulations(w_pref):
    """
    Sw: Move any two distinct men to top of w's list in any order.
    """
    manipulations = []
    # print(len(list(itertools.permutations(w_pref, 2))))
    for mi, mj in itertools.permutations(w_pref, 2): 
        rest = [m for m in w_pref if m != mi and m != mj]
        new_pref = [mi, mj] + rest
        manipulations.append(new_pref)
    return manipulations


def generate_sm_manipulations(m_pref, mu_m):
    """
    Sm: Promote µ(m) to top, then for every other woman, promote her to top of that list.
    """
    sm = []
    bm = [mu_m] + [w for w in m_pref if w != mu_m]
    sm.append(bm)

    for w0 in bm[1:]:  # exclude mu(m) which is already at the top
        manipulated = [w0] + [w for w in bm if w != w0]
        sm.append(manipulated)

    return sm


def two_for_one(mpref, wpref, accomplice, beneficiary):
    initial_matching = gale_shapley(mpref, wpref)
    mpref_prime = copy.deepcopy(mpref)
    wpref_prime = copy.deepcopy(wpref)
    best_matching = initial_matching

    accomplice_pref = mpref[accomplice - 1] 
    beneficiary_pref = wpref[beneficiary - 1]

    Sw = generate_sw_manipulations(beneficiary_pref)

    for w_misreport in Sw:
        t5 = time.perf_counter()

        Sm = generate_sm_manipulations(accomplice_pref, initial_matching[accomplice - 1])

        for m_misreport in Sm:
            t6 = time.perf_counter()
            mpref_prime[accomplice - 1] = m_misreport 
            wpref_prime[beneficiary - 1] = w_misreport
            new_matching = gale_shapley(mpref_prime, wpref_prime)

            new_w_pairing = new_matching[beneficiary - 1]
            new_m_pairing = new_matching[accomplice - 1]

            if beneficiary_pref.index(new_w_pairing) < beneficiary_pref.index(initial_matching[beneficiary - 1]) and initial_matching[accomplice - 1] == new_m_pairing:
                best_matching = new_matching
                accomplice_pref = m_misreport
                beneficiary_pref = w_misreport
        t7 = time.perf_counter()
        # print(f"Time for t5 - t6: {t6 - t5:.4f} seconds")
        # print(f"Time for t6 - t7: {t7 - t6:.4f} seconds")
    return accomplice_pref, beneficiary_pref, best_matching

#!/usr/bin/env python3
# hpc_two_for_one.py
"""
Fast evaluation of two_for_one() on an HPC node.
Parallelism:
  • outer loop over CSV rows  → sequential (usually only a few rows)
  • inner two_for_one calls   → ProcessPool across the CPUs
"""

#!/usr/bin/env python3
# hpc_two_for_one.py  (tqdm-free version)
"""
Fast evaluation of two_for_one() on an HPC node.

Parallelism
-----------
• Outer loop over CSV rows  → sequential (usually only a few rows)
• Inner two_for_one calls   → ProcessPool spread across CPUs
"""

#!/usr/bin/env python3
"""
two_for_one.py  –  HPC-friendly evaluation script
=================================================
Runs every two_for_one() combination in parallel **inside one node**.
Submit with:

    sbatch run_two_for_one.sbatch

where run_two_for_one.sbatch contains the SLURM options you showed.
"""

#!/usr/bin/env python3
"""
two_for_one.py            (timestamp + live-concurrency version)
================================================================
Run this exactly as in your SBATCH script:
    python3 -u two_for_one.py
The script looks for 'euclidean_mallows_accomplice.csv' in the same
directory.  Edit CSV_NAME below if needed.
"""

import csv, json, itertools, os, sys, time, threading
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path

# ----------------------------------------------------------------------
# 0.  Config
# ----------------------------------------------------------------------
CSV_NAME = "expectations_euclidean_accomplice.csv"   # file sits next to script
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

# ----------------------------------------------------------------------
# 2.  Pool‐initializer: broadcast big objects + shared counter
# ----------------------------------------------------------------------
def _init_pool(shared_mpref, shared_wpref, shared_orig, active_ctr):
    global MPREF, WPREF, ORIGINAL, ACTIVE
    MPREF, WPREF, ORIGINAL, ACTIVE = (
        shared_mpref, shared_wpref, shared_orig, active_ctr
    )

# ----------------------------------------------------------------------
# 3.  Worker: exactly one two_for_one() call
# ----------------------------------------------------------------------
def _pair_worker(pair):
    accomplice, beneficiary = pair
    ACTIVE.value += 1                 # -------- start
    try:
        *_, new_match = two_for_one(MPREF, WPREF, accomplice, beneficiary)
        return int(new_match != ORIGINAL)
    finally:
        ACTIVE.value -= 1             # -------- done

# ----------------------------------------------------------------------
# 4.  Detect how many CPUs SLURM gave us
# ----------------------------------------------------------------------
def detect_worker_count() -> int:
    for v in ("SLURM_CPUS_PER_TASK", "SLURM_NTASKS_PER_NODE", "SLURM_NTASKS"):
        if v in os.environ and os.environ[v].isdigit():
            return int(os.environ[v])
    return os.cpu_count()

# ----------------------------------------------------------------------
# 5.  Main
# ----------------------------------------------------------------------
def run():
    workers = detect_worker_count()
    print(f"[INFO] Using {workers} worker processes", flush=True)

    csv_path = Path(__file__).resolve().parent / CSV_NAME
    if not csv_path.exists():
        sys.exit(f"[ERROR] CSV not found: {csv_path}")

    wall_start = time.time()
    all_results = defaultdict(list)

    results_saver = [['Dimension', 'STD', 'Mprefs', 'Wprefs', 'Sample', 'Count_woman', 'Count_pairs', 'Two_for_one']]

    with csv_path.open(newline="") as fh:
        reader = csv.reader(fh)
        hdr = next(reader)

        for row_idx, row in enumerate(reader, 1):
            if row_idx%500 > 99: continue
            dimension, std = int(row[0]), float(row[1])
            mpref, wpref = map(json.loads, row[2:4])
            original = gale_shapley(mpref, wpref)
            #if dimension > ___: break

            # Build task list for this row
            pairs = list(itertools.product(
                range(1, len(mpref) + 1),
                range(1, len(wpref) + 1)
            ))
            n_pairs = len(pairs)
            print(f"[row {row_idx}] (dimension={dimension}, std={std}) "
                  f"→ {n_pairs:,} two_for_one calls")

            # Shared “currently running” counter
            active_ctr = mp.Value('i', 0)

            # Progress printer thread
            processed = 0
            def progress():
                last = time.time()
                while processed < n_pairs:
                    if time.time() - last >= 2:          # every 2 s
                        print(f"[{time.strftime('%X')}] "
                              f"finished: {processed:,}/{n_pairs:,}   "
                              f"running now: {active_ctr.value}",
                              flush=True)
                        last = time.time()
                    time.sleep(0.2)
                # final line
                print(f"[{time.strftime('%X')}] "
                      f"finished: {processed:,}/{n_pairs:,}   "
                      f"running now: 0", flush=True)
            t_pr = threading.Thread(target=progress, daemon=True)
            t_pr.start()

            hits = 0
            chunksz = max(1, n_pairs // (8 * workers))

            with mp.Pool(
                processes=workers,
                initializer=_init_pool,
                initargs=(mpref, wpref, original, active_ctr),
            ) as pool:
                for hit in pool.imap_unordered(_pair_worker, pairs,
                                               chunksize=chunksz):
                    hits += hit
                    processed += 1

            t_pr.join()       # ensure last progress line prints
            all_results[(dimension, std)].append(hits)
            print(f"[row {row_idx}] success_count = {hits:,}\n", flush=True)
            row.append(hits)
            results_saver.append(row)

    with open(f'two_for_one_results_expectations_euclidean.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(results_saver)    

    # Aggregate
    print("\nAverages across repeats:")
    for (dim, stan), lst in all_results.items():
        avg = sum(lst) / len(lst)
        print(f"  (dimension={dim:.3g}, std={stan:.3g}) → {avg:,.0f}")

    print(f"\nTotal wall-clock time: {time.time() - wall_start:.1f} s")

# ----------------------------------------------------------------------
# 6.  Entry-point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    try:
        run()
    except KeyboardInterrupt:
        sys.stderr.write("\n[WARN] Interrupted by user — terminating.\n")
        sys.exit(1)






