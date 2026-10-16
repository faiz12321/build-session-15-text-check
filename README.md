# Check a fictional text file

Save three source files in a NEW empty lesson folder.

    python make_sample.py
    python textcheck.py sample/mixed.txt
    python -m unittest -v

Two Windows and two Ubuntu full replays run exact visible source versions. Final 39 small fixture tests pass (Unix pipe skips on Windows); symlink creation can skip where unavailable. Displayed stdout is first Windows output, not normalized or mixed. Pair differences are unittest time.
Only link/error changes: final reader refuses input/ancestor symbolic links/reparse points, hardlinks, special files and traversal before reading. Metadata/open errors remain exit 2. Setup refuses linked parents/traversal and existing sample paths, without reset or deletion. Naive first version remains fictional-sample-only and must be replaced.
Original raw-byte analysis, line-ending counts, LF-based line numbering, BOM/tab notes, trailing-space, NUL, final-newline and UTF-8 rules remain unchanged. Exits remain 0 no reported problems, 1 reported problems, 2 usage/read errors. A pass is not file-type, meaning, content safety or other-program acceptance proof. Tabs and BOM alone remain notes, not failures.
The checker has no write/move/delete/network code but reads the entire file into memory. No size/time/resource limit, atomic snapshot or hostile-race defense. Stop editors/sync. Paths can be private. Small fictional fixtures are not proof on every filesystem. No desktop Windows/macOS recording. Recorder removes only its own temporary fixture folder. Decisions and feedback are teaching text, not recorded output.

MIT code. Python separately licensed/not included.

Reference: https://docs.python.org/3/library/os.html

Windows pair: https://github.com/faiz12321/lesson-lab/actions/runs/38973259376
Ubuntu pair: https://github.com/faiz12321/lesson-lab/actions/runs/38973407351
