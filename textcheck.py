"""Reads one text file as raw bytes and reports its line endings, tabs,
trailing spaces, final newline, NUL bytes and whether it is valid UTF-8.
It does not change any file.

Run: python textcheck.py FILE
Exit code: 0 = no problems found by these checks, 1 = problems, 2 = could not read.
"""
import sys

SHOW = 5
BOM = b"\xef\xbb\xbf"


def check(path):
    with open(path, "rb") as f:
        data = f.read()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    r = {"bytes": len(data), "lines": len(lines), "crlf": crlf, "lf": lf,
         "cr": cr, "bom": data.startswith(BOM),
         "final_newline": data == b"" or data.endswith(b"\n"),
         "tabs": [], "trailing": [], "nul": [], "utf8_error": None}
    for number, line in enumerate(lines, 1):
        if b"\t" in line:
            r["tabs"].append(number)
        body = line[:-1] if line.endswith(b"\r") else line
        if body.endswith((b" ", b"\t")):
            r["trailing"].append(number)
        if b"\x00" in line:
            r["nul"].append(number)
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as e:
        r["utf8_error"] = (data.count(b"\n", 0, e.start) + 1, e.start)
    return r


def first(numbers):
    shown = ", ".join(str(n) for n in numbers[:SHOW])
    more = f" and {len(numbers) - SHOW} more" if len(numbers) > SHOW else ""
    return shown + more


def report(r):
    print("Size:", r["bytes"], "bytes,", r["lines"], "lines")
    print(f"Line endings: {r['crlf']} Windows (CRLF), {r['lf']} Unix (LF), {r['cr']} lone CR")
    if r["bom"]:
        print("Note: the file starts with a UTF-8 byte order mark.")
    if r["tabs"]:
        print(f"Note: lines with a tab: {len(r['tabs'])} (line numbers: {first(r['tabs'])}).")
    problems = []
    if (r["crlf"] and r["lf"]) or r["cr"]:
        problems.append("Mixed or unusual line endings: the file does not use one kind throughout.")
    if r["trailing"]:
        problems.append(f"Lines that end with a space or tab: {len(r['trailing'])} (line numbers: {first(r['trailing'])}).")
    if not r["final_newline"]:
        problems.append("The last line has no line ending.")
    if r["nul"]:
        problems.append(f"Lines that contain a NUL byte: {len(r['nul'])} (line numbers: {first(r['nul'])}).")
    if r["utf8_error"]:
        line, offset = r["utf8_error"]
        problems.append(f"Not valid UTF-8: first bad byte at offset {offset}, on line {line}.")
    for p in problems:
        print("Problem:", p)
    if not problems:
        print("No problems found by these checks.")
    return 1 if problems else 0


def main(argv):
    if len(argv) != 2:
        print("Usage: python textcheck.py FILE")
        return 2
    try:
        result = check(argv[1])
    except OSError as e:
        print("Could not read the file:", e)
        return 2
    return report(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
