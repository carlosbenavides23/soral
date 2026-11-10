import contextlib, io, json, os, socket, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from soral.cli import main
from soral.contracts import ResultError, TargetResult, render, sanitize

class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        p = patch.dict(os.environ, {"SORAL_CONFIG_HOME": self.tmp.name}); p.start(); self.addCleanup(p.stop)
    def call(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            try: code = main(args)
            except SystemExit as exc: code = exc.code
        return code, out.getvalue(), err.getvalue()
    def test_help_version_invalid(self):
        for args in (["--help"], ["--version"]):
            code, out, err = self.call(args); self.assertEqual(code, 0); self.assertTrue(out); self.assertEqual(err, "")
        code, out, err = self.call(["scan", "https://example.invalid"])
        self.assertEqual(code, 2); self.assertEqual(out, ""); self.assertTrue(err)
    def test_config_formats(self):
        self.assertEqual(self.call(["config", "set", "warning", "false"]), (0, "", ""))
        for fmt in ("json", "jsonl"):
            code, out, err = self.call(["config", "show", "--format", fmt])
            self.assertEqual((code, err), (0, "")); self.assertEqual(json.loads(out), {"warning": False}); self.assertEqual(len(out.splitlines()), 1)
            self.assertEqual(json.loads(self.call(["version", "--format", fmt])[1])["schema_version"], "1")
    def test_invalid_config(self):
        path = Path(self.tmp.name) / "soral" / "config.toml"; path.parent.mkdir(); path.write_text("warning = [", encoding="utf-8")
        code, out, err = self.call(["config", "show"]); self.assertEqual(code, 2); self.assertEqual(out, ""); self.assertTrue(err)
        code, out, err = self.call(["config", "set", "warning", "maybe"]); self.assertEqual(code, 2); self.assertEqual(out, ""); self.assertTrue(err)
    def test_contract_controls(self):
        obj = TargetResult("example", ResultError("blocked", "no"))
        self.assertEqual(json.loads(render(obj, "json"))["error"]["code"], "blocked")
        self.assertNotIn("\x1b", sanitize("x\x1b[31m\n")); self.assertNotIn("\n", sanitize("x\n"))
if __name__ == "__main__": unittest.main()
