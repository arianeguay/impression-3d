"""watch.py pushes one "check failed" per run of failed checks, not one per check (HOM-1358).

    python3 -m unittest discover tests
"""
import os, sys, tempfile, unittest
from unittest import mock

# printer.py reads ~/.config/impression-3d/printer.env at import, and its op:// values call `op`.
os.environ["HOME"] = tempfile.mkdtemp()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import watch  # noqa: E402


class CheckFailedTest(unittest.TestCase):
    def run_watch(self, judge_results):
        """Runs main() over one loop iteration per entry: an exception is raised, a dict returned."""
        gcode = tempfile.NamedTemporaryFile("w", suffix=".gcode", delete=False)
        gcode.write("; printing object part_a\n")
        gcode.close()
        self.addCleanup(os.unlink, gcode.name)
        details = [{"detail": {"status": "printing", "printProgress": 0.1}}] * len(judge_results)
        details.append({"detail": {"status": "ready", "printProgress": 1.0}})
        pushed = []

        def judge(*_):
            r = judge_results.pop(0)
            if isinstance(r, Exception):
                raise r
            return r, "part_a", 1.0

        with mock.patch.object(watch.printer, "http", side_effect=details), \
                mock.patch.object(watch, "judge", side_effect=judge), \
                mock.patch.object(watch, "notify", side_effect=lambda _c, t, _m: pushed.append(t)), \
                mock.patch.object(watch.time, "sleep"), \
                mock.patch.object(sys, "argv", ["watch.py", gcode.name, "--notify", "true"]):
            watch.main()
        return [t for t in pushed if t == "Print watch: check failed"]

    def test_five_failed_checks_push_once(self):
        refused = OSError("<urlopen error [Errno 111] Connection refused>")
        self.assertEqual(len(self.run_watch([refused] * 5)), 1)

    def test_a_success_rearms_the_alert(self):
        refused = OSError("refused")
        ok = {"verdict": "ok", "reason": "fine"}
        self.assertEqual(len(self.run_watch([refused, refused, ok, refused, refused])), 2)


if __name__ == "__main__":
    unittest.main()
