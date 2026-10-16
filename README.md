# Check a text file's line endings and spacing

A small read-only Python tool built step by step. Give it one text file and it reads the raw bytes and reports how many lines end the Windows way (CRLF) and the Unix way (LF), lone CR characters, lines that contain a tab, lines that end with a space or tab, a missing line ending on the last line, NUL bytes, a UTF-8 byte order mark, and whether the bytes are valid UTF-8. It has no code that writes to a file.

## Run it

    python make_sample.py                   # makes made-up files in sample/
    python textcheck.py sample/mixed.txt    # report on one file
    python -m unittest -v                   # 27 temporary-fixture tests

On Windows, if `python` is not found, use `py`.

## Files

- `textcheck.py` - the tool
- `make_sample.py` - makes four made-up files: Unix endings, Windows endings, mixed, and one that is not UTF-8
- `test_textcheck.py` - tests

## Notes

- The file is read as bytes, so nothing is translated on the way in. Python's text mode can translate line endings when it reads a file (https://docs.python.org/3/library/io.html), which is why this tool does not use it.
- One kind of line ending throughout passes, whether it is CRLF or LF. The tool reports mixed endings and lone CR characters as a problem. It does not say which kind another program expects.
- Tabs are reported as a note only, not a problem.
- Lines are counted by the LF character. A lone CR is counted separately and does not start a new line in the tool's count.
- The first five line numbers of each kind are shown, with the total.
- It checks for NUL bytes and valid UTF-8 only. A file that is valid UTF-8 can still hold text in a different encoding that happens to look valid.
- "No problems found by these checks" only means those checks passed.
- Tested only on small made-up files. Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop.
- Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.

## Setup safety and evidence

Setup refuses every existing sample path and exclusively writes four fictional text files in a new folder. It does not replace or delete old data. Start in a new empty lesson folder; do not delete old work to force a retry. Four setup collision/repeat/CLI tests check preservation of unrelated nested bytes and modification times. The checker is unchanged. It reads all bytes and creates an in-memory line list, so large files can use substantial memory. Input links are followed. Reports can reveal names, paths, line numbers and errors; keep private output private. This is not a security scanner or encoding detector. Concurrent hostile filesystem changes are outside the tested scope.

Two Windows and two Ubuntu full replays pass 27 tests. Each platform pair differs only in unittest time. Displays use first Windows output. The recorder writes exact visible first/final versions into a unique temporary folder and removes only that folder. Setup itself refuses repeat runs. Phone interactions and 320/390/1280 layout checks pass. These are limited fictional-fixture checks, not real-file or desktop tests.
