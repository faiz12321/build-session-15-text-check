"""Makes four small made-up text files to practise on.

Run: python make_sample.py
"""
from pathlib import Path

FILES = {
    "unix.txt": b"first line\nsecond line\nthird line\n",
    "windows.txt": b"first line\r\nsecond line\r\nthird line\r\n",
    "mixed.txt": b"first line\r\nsecond line \nthird\tline\nlast line",
    "latin1.txt": b"caf\xe9 menu\nsecond line\n",
}


def make(folder):
    folder = Path(folder)
    folder.mkdir()
    for name, data in FILES.items():
        with (folder / name).open("xb") as handle:
            handle.write(data)
    return folder


if __name__ == "__main__":
    try:
        make("sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print("Made sample/unix.txt, windows.txt, mixed.txt and latin1.txt")
