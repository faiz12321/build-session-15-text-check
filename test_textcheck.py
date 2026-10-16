from unittest import mock
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import make_sample
import textcheck


def check_bytes(data):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "f.txt")
        p.write_bytes(data)
        return textcheck.check(str(p))


def run_main(data=None, args=None):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "f.txt")
        if data is not None:
            p.write_bytes(data)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = textcheck.main(["textcheck.py"] + (args if args is not None else [str(p)]))
    return rc, buf.getvalue()


class CountTests(unittest.TestCase):
    def test_unix_endings(self):
        r = check_bytes(b"a\nb\n")
        self.assertEqual((r["lf"], r["crlf"], r["cr"], r["lines"]), (2, 0, 0, 2))

    def test_windows_endings(self):
        r = check_bytes(b"a\r\nb\r\n")
        self.assertEqual((r["lf"], r["crlf"], r["cr"], r["lines"]), (0, 2, 0, 2))

    def test_lone_cr(self):
        r = check_bytes(b"a\rb\r")
        self.assertEqual((r["lf"], r["crlf"], r["cr"]), (0, 0, 2))

    def test_crcrlf_counts_one_lone_cr(self):
        r = check_bytes(b"a\r\r\n")
        self.assertEqual((r["crlf"], r["cr"]), (1, 1))

    def test_empty_file(self):
        r = check_bytes(b"")
        self.assertEqual((r["lines"], r["final_newline"]), (0, True))

    def test_final_newline_missing(self):
        self.assertFalse(check_bytes(b"a\nb")["final_newline"])
        self.assertEqual(check_bytes(b"a\nb")["lines"], 2)

    def test_blank_last_line_counts(self):
        self.assertEqual(check_bytes(b"a\n\n")["lines"], 2)

    def test_tabs_listed_with_line_numbers(self):
        self.assertEqual(check_bytes(b"a\nb\tc\n\td\n")["tabs"], [2, 3])

    def test_trailing_space_and_tab(self):
        self.assertEqual(check_bytes(b"a \nb\t\nc\n")["trailing"], [1, 2])

    def test_trailing_space_before_crlf(self):
        self.assertEqual(check_bytes(b"a \r\nb\r\n")["trailing"], [1])

    def test_line_of_only_spaces_is_trailing(self):
        self.assertEqual(check_bytes(b"   \n")["trailing"], [1])

    def test_nul_byte_found(self):
        self.assertEqual(check_bytes(b"a\nb\x00c\n")["nul"], [2])

    def test_bom_detected(self):
        self.assertTrue(check_bytes(b"\xef\xbb\xbfa\n")["bom"])
        self.assertFalse(check_bytes(b"a\n")["bom"])

    def test_utf8_error_position(self):
        r = check_bytes(b"ab\ncaf\xe9\n")
        self.assertEqual(r["utf8_error"], (2, 6))

    def test_valid_utf8_with_accents(self):
        self.assertIsNone(check_bytes("caf\u00e9\n".encode("utf-8"))["utf8_error"])


class ReportTests(unittest.TestCase):
    def test_one_kind_of_ending_passes_either_way(self):
        for data in (b"a\nb\n", b"a\r\nb\r\n"):
            rc, out = run_main(data)
            self.assertEqual(rc, 0)
            self.assertIn("No problems found by these checks.", out)

    def test_mixed_endings_is_a_problem(self):
        rc, out = run_main(b"a\r\nb\n")
        self.assertEqual(rc, 1)
        self.assertIn("Mixed or unusual line endings", out)

    def test_tabs_alone_are_only_a_note(self):
        rc, out = run_main(b"a\tb\n")
        self.assertEqual(rc, 0)
        self.assertIn("Note: lines with a tab: 1", out)

    def test_only_first_five_shown_with_total(self):
        rc, out = run_main(b"x \n" * 8)
        self.assertIn("Lines that end with a space or tab: 8", out)
        self.assertIn("and 3 more", out)

    def test_missing_file_exit_two(self):
        rc, out = run_main(args=["no-such-file.txt"])
        self.assertEqual(rc, 2)

    def test_wrong_arguments_exit_two(self):
        rc, out = run_main(args=[])
        self.assertEqual(rc, 2)


class SampleTests(unittest.TestCase):
    def test_sample_files_report_as_described(self):
        with tempfile.TemporaryDirectory() as d:
            folder = make_sample.make(Path(d, "sample"))
            unix = textcheck.check(str(folder / "unix.txt"))
            win = textcheck.check(str(folder / "windows.txt"))
            mixed = textcheck.check(str(folder / "mixed.txt"))
            latin = textcheck.check(str(folder / "latin1.txt"))
        self.assertEqual((unix["lf"], unix["crlf"]), (3, 0))
        self.assertEqual((win["lf"], win["crlf"]), (0, 3))
        self.assertEqual((mixed["crlf"], mixed["lf"], mixed["tabs"], mixed["trailing"], mixed["final_newline"]), (1, 2, [3], [2], False))
        self.assertEqual(latin["utf8_error"], (1, 3))

    def test_checking_does_not_change_the_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "f.txt")
            p.write_bytes(b"a \r\nb\n")
            os.utime(p, (1_000_000_000, 1_000_000_000))
            before = (p.read_bytes(), p.stat().st_mtime)
            textcheck.check(str(p))
            after = (p.read_bytes(), p.stat().st_mtime)
        self.assertEqual(before, after)


class SetupSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sample = self.root / 'sample'

    def test_existing_folder_preserves_nested_bytes_and_metadata(self):
        (self.sample / 'nested').mkdir(parents=True)
        keep = self.sample / 'nested' / 'keep.bin'
        keep.write_bytes(b'KEEP')
        before = (keep.read_bytes(), keep.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (keep.read_bytes(), keep.stat().st_mtime_ns))
        self.assertEqual(sorted(p.relative_to(self.sample).as_posix() for p in self.sample.rglob('*')), ['nested','nested/keep.bin'])

    def test_existing_file_preserved(self):
        self.sample.write_bytes(b'KEEP')
        before = (self.sample.read_bytes(), self.sample.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, (self.sample.read_bytes(), self.sample.stat().st_mtime_ns))

    def test_repeat_setup_preserves_generated_bytes_and_metadata(self):
        make_sample.make(self.sample)
        before = {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()}
        with self.assertRaises(FileExistsError):
            make_sample.make(self.sample)
        self.assertEqual(before, {p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.sample.iterdir()})

    def test_cli_refuses_without_replacing(self):
        import shutil, subprocess, sys
        script = self.root / 'make_sample.py'
        shutil.copyfile(Path(__file__).resolve().parent / 'make_sample.py', script)
        self.sample.mkdir()
        keep = self.sample / 'keep'
        keep.write_bytes(b'KEEP')
        result = subprocess.run([sys.executable,str(script)],capture_output=True,text=True,cwd=self.root)
        self.assertEqual(result.returncode,1)
        self.assertIn('Nothing was replaced or deleted',result.stderr)
        self.assertEqual(keep.read_bytes(),b'KEEP')






class PathSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'sample'
        make_sample.make(self.root);self.file=self.root/'unix.txt'
    def link(self,path,target,directory=False):
        try:path.symlink_to(target,target_is_directory=directory)
        except OSError:self.skipTest('Symlink creation unavailable')
    def code(self,path):
        with redirect_stdout(io.StringIO()) as out:code=textcheck.main(['textcheck.py',str(path)])
        return code,out.getvalue()
    def test_file_link_refuses(self):
        p=self.base/'linked';self.link(p,self.file)
        with self.assertRaises(OSError):textcheck.safe_input(p)
        self.assertEqual(self.code(p)[0],2)
    def test_linked_ancestor_refuses(self):
        p=self.base/'linked';self.link(p,self.root,True)
        self.assertEqual(self.code(p/'unix.txt')[0],2)
    def test_dangling_link_refuses(self):
        p=self.base/'linked';self.link(p,self.base/'missing')
        self.assertEqual(self.code(p)[0],2)
    def test_self_loop_refuses(self):
        p=self.base/'linked';self.link(p,p)
        self.assertEqual(self.code(p)[0],2)
    def test_hardlink_refuses(self):
        p=self.base/'hard';os.link(self.file,p)
        self.assertEqual(self.code(p)[0],2)
    def test_pipe_refuses_without_blocking(self):
        if not hasattr(os,'mkfifo'):self.skipTest('Unix pipe unavailable')
        p=self.base/'pipe';os.mkfifo(p)
        self.assertEqual(self.code(p)[0],2)
    def test_directory_refuses(self):self.assertEqual(self.code(self.root)[0],2)
    def test_traversal_refuses(self):self.assertEqual(self.code(self.root/'..'/'sample'/'unix.txt')[0],2)
    def test_reparse_attribute_refuses(self):
        real=Path.lstat;target=self.file
        def fake(path,*args,**kwargs):
            value=real(path,*args,**kwargs)
            if path==target:return type('Reparse',(),{'st_mode':value.st_mode,'st_file_attributes':0x400})()
            return value
        with mock.patch.object(Path,'lstat',fake):self.assertEqual(self.code(self.file)[0],2)
    def test_metadata_failure_nonzero(self):
        with mock.patch.object(Path,'lstat',side_effect=OSError('forced metadata error')):
            code,text=self.code(self.file);self.assertEqual(code,2);self.assertIn('forced metadata error',text)
    def test_setup_linked_parent_refuses(self):
        p=self.base/'linked';self.link(p,self.root,True)
        with self.assertRaises(OSError):make_sample.make(p/'new')
        self.assertFalse((self.root/'new').exists())
    def test_setup_traversal_refuses(self):
        with self.assertRaises(OSError):make_sample.make(self.root/'..'/'new')



if __name__ == "__main__":
    unittest.main()
