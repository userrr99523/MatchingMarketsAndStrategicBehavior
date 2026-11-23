#!/usr/bin/env python3
"""
batch_push.py - commit and push a large number of files to GitHub in batches.

Run it from the root of your git repo (e.g. in VS Code's terminal):

    python batch_push.py                      # default: ~500 MB / 1000 files per push
    python batch_push.py --max-mb 300 --max-files 500
    python batch_push.py --dry-run            # preview the batches without committing

What it does:
  * Finds every new, modified, or deleted file Git sees (respects .gitignore).
  * Skips files over GitHub's 100 MB limit (and lists them so you can use
    Git LFS or store them elsewhere) unless they are tracked by Git LFS.
  * Groups the rest into batches under the size / count limits.
  * For each batch: git add -> git commit -> git push.
  * Stops on the first failed push so nothing gets out of sync.
"""

import argparse
import os
import subprocess
import sys

GITHUB_HARD_LIMIT = 100 * 1024 * 1024  # 100 MiB


def git(*args, input_bytes=None, check=True):
    result = subprocess.run(
        ["git", *args], input=input_bytes, capture_output=True
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        raise SystemExit(f"\n'git {' '.join(args)}' failed; stopping.")
    return result


def pending_files():
    """New (untracked, not ignored), modified, and deleted files, NUL-separated."""
    out = git("ls-files", "--others", "--modified", "--deleted",
              "--exclude-standard", "-z").stdout
    files = [p for p in out.decode(errors="surrogateescape").split("\0") if p]
    return sorted(set(files))  # modified+deleted can list a path twice


def lfs_tracked(paths):
    """Return the subset of paths that .gitattributes routes to Git LFS."""
    if not paths:
        return set()
    data = "\0".join(paths).encode(errors="surrogateescape") + b"\0"
    out = git("check-attr", "-z", "--stdin", "filter",
              input_bytes=data, check=False).stdout.decode(errors="surrogateescape")
    parts = out.split("\0")
    tracked = set()
    for i in range(0, len(parts) - 2, 3):
        path, _attr, value = parts[i], parts[i + 1], parts[i + 2]
        if value == "lfs":
            tracked.add(path)
    return tracked


def make_batches(files, max_bytes, max_files):
    lfs = lfs_tracked(files)
    batches, current, current_size, too_big = [], [], 0, []
    for path in files:
        size = os.path.getsize(path) if os.path.isfile(path) else 0
        if size > GITHUB_HARD_LIMIT and path not in lfs:
            too_big.append((path, size))
            continue
        if current and (current_size + size > max_bytes or len(current) >= max_files):
            batches.append(current)
            current, current_size = [], 0
        current.append(path)
        current_size += size
    if current:
        batches.append(current)
    return batches, too_big


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-mb", type=float, default=500,
                    help="max total size per push in MB (default 500; GitHub caps a push at 2 GB)")
    ap.add_argument("--max-files", type=int, default=1000,
                    help="max number of files per push (default 1000)")
    ap.add_argument("--message", default="Batch upload",
                    help="commit message prefix (default 'Batch upload')")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--dry-run", action="store_true",
                    help="show the batches without committing or pushing")
    args = ap.parse_args()

    if git("rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise SystemExit("Not inside a git repository. cd into your repo first.")

    files = pending_files()
    if not files:
        print("Nothing to commit - working tree is clean.")
        return

    batches, too_big = make_batches(files, args.max_mb * 1024 * 1024, args.max_files)

    if too_big:
        print("Skipping files over GitHub's 100 MB limit (use Git LFS or store elsewhere):")
        for path, size in too_big:
            print(f"  {size / 1024 / 1024:8.1f} MB  {path}")
        print()

    print(f"{sum(len(b) for b in batches)} files in {len(batches)} batch(es).")
    if args.dry_run:
        for i, batch in enumerate(batches, 1):
            size = sum(os.path.getsize(p) for p in batch if os.path.isfile(p))
            print(f"  Batch {i}: {len(batch)} files, {size / 1024 / 1024:.1f} MB")
        return

    for i, batch in enumerate(batches, 1):
        data = "\0".join(batch).encode(errors="surrogateescape") + b"\0"
        git("add", "-A", "--pathspec-from-file=-", "--pathspec-file-nul",
            input_bytes=data)
        git("commit", "-m", f"{args.message} ({i}/{len(batches)})")
        print(f"Pushing batch {i}/{len(batches)} ({len(batch)} files)...", flush=True)
        git("push", "-u", args.remote, "HEAD")
    print("Done - all batches pushed.")


if __name__ == "__main__":
    main()
