#!/usr/bin/env python3
"""Entry point: copy the pre-rendered entry.png to $MAKEFUN_OUTPUT_DIR.

Standard library only. The image is rendered at build time by draw.py;
this program only copies it, and verifies the copy byte for byte."""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        sys.stderr.write("MAKEFUN_OUTPUT_DIR is not set\n")
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(SRC, "rb") as f:
        want = hashlib.sha256(f.read()).hexdigest()
    shutil.copyfile(SRC, dst)
    with open(dst, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != want:
        sys.stderr.write("entry.png copy failed verification\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
