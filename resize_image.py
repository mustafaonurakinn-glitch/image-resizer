#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import uuid
from pathlib import Path
from PIL import Image


def parse_size(size_str: str):
    # Only accepts exact sizes like: 100x100
    try:
        w, h = size_str.lower().split("x", 1)
        w, h = int(w), int(h)
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except Exception:
        raise ValueError('Size must be in "WIDTHxHEIGHT" format (e.g. 100x100)')


def atomic_save(image: Image.Image, target_path: Path):
    """
    Save to a temp file then atomically replace the target.
    This prevents corrupted output if two processes write same target simultaneously.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    #tmp_path = target_path.with_suffix(target_path.suffix + f".tmp-{uuid.uuid4().hex}")
    tmp_path = target_path.with_name(f"{target_path.stem}_tmp_{uuid.uuid4().hex}{target_path.suffix}")


    image.save(tmp_path)
    os.replace(tmp_path, target_path)  # atomic on Windows


def resize_and_save(src: Path, dst: Path, width: int, height: int):
    with Image.open(src) as im:
        resized = im.resize((width, height), Image.LANCZOS)

        # JPEG alpha fix
        if dst.suffix.lower() in (".jpg", ".jpeg"):
            if resized.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", resized.size, (255, 255, 255))
                bg.paste(resized, mask=resized.split()[-1])
                resized = bg
            elif resized.mode != "RGB":
                resized = resized.convert("RGB")

        atomic_save(resized, dst)


def main():
    # 3 params: source, size, target
    if len(sys.argv) != 4:
        print(
            "Usage:\n"
            "  resize_image.exe <source_path> <WIDTHxHEIGHT> <target_path>\n"
            "Example:\n"
            "  resize_image.exe C:\\imgs\\a.png 300x300 C:\\out\\a.png",
            file=sys.stderr,
        )
        sys.exit(1)

    source_path = Path(sys.argv[1]).expanduser().resolve()
    size_str = sys.argv[2]
    target_path = Path(sys.argv[3]).expanduser().resolve()

    if not source_path.exists():
        print(f"Source file not found: {source_path}", file=sys.stderr)
        sys.exit(2)

    try:
        width, height = parse_size(size_str)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(3)

    try:
        resize_and_save(source_path, target_path, width, height)
    except Exception as e:
        print(f"Resize failed: {e}", file=sys.stderr)
        sys.exit(4)

    # return path via stdout
    print(str(target_path))


if __name__ == "__main__":
    main()
