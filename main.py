#!/usr/bin/env python3
"""Entrypoint: copy entry.png to $MAKEFUN_OUTPUT_DIR (stdlib only).

The grader runs this on a read-only filesystem with MAKEFUN_OUTPUT_DIR
set to a writable directory. Never write to os.getcwd().
"""
import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        sys.stderr.write("MAKEFUN_OUTPUT_DIR is not set\n")
        return 1
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
