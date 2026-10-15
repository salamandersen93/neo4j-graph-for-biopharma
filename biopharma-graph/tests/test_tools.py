import os, sys, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "model"))
import queries as lib, run_queries as rq

class Splitter(unittest.TestCase):
    def test_basic(self): self.assertEqual(rq.split_statements("RETURN 1; RETURN 2;"), ["RETURN 1", "RETURN 2"])
    def test_semicolon_in_string(self): self.assertEqual(rq.split_statements("RETURN 'a;b'; RETURN 2"), ["RETURN 'a;b'", "RETURN 2"])
    def test_comments_dropped(self): self.assertEqual(rq.split_statements("// x; y\nRETURN 1; /* ; */ RETURN 2"), ["RETURN 1", "RETURN 2"])
    def test_backticks(self): self.assertEqual(rq.split_statements("DROP INDEX `a;b` IF EXISTS;"), ["DROP INDEX `a;b` IF EXISTS"])
    def test_every_library_query_splits(self):
        for s in lib.sections():
            for k, q in s["items"]:
                if k == "query": self.assertTrue(rq.split_statements(q.body), q.file)

class Library(unittest.TestCase):
    def test_lint_clean(self):
        e, w = lib.lint(); self.assertEqual(e, [], e)
    def test_ids_unique_and_ordered_within_files(self):
        ids = [q.id for s in lib.sections() for k, q in s["items"] if k == "query"]
        self.assertEqual(len(ids), len(set(ids)))
    def test_docs_render(self):
        text, flat = lib.render(); self.assertIn("### Q01", text); self.assertEqual(len(flat), len(set(q.id for q in flat)))

class FakeResult:
    def __init__(self, n): self.n = n
    def __iter__(self): return iter(range(self.n))
    def consume(self): pass
class FakeSession:
    def __init__(self, fail_on=None): self.log, self.fail_on = [], fail_on
    def run(self, stmt):
        self.log.append(stmt)
        if self.fail_on and self.fail_on in stmt: raise RuntimeError("boom\nsecond line")
        return FakeResult(3)

def q_by_id(i):
    return next(q for s in lib.sections() for k, q in s["items"] if k == "query" and q.id == i)

class Runner(unittest.TestCase):
    def test_write_query_skipped_by_default(self):
        s = FakeSession(); st, _ = rq.run_one(s, q_by_id("Q20"), allow_writes=False); self.assertEqual(st, "SKIP"); self.assertEqual(s.log, [])
    def test_write_query_runs_then_undoes(self):
        s = FakeSession(); st, _ = rq.run_one(s, q_by_id("Q20"), allow_writes=True)
        self.assertEqual(st, "PASS"); self.assertIn("MERGE", s.log[0]); self.assertIn("DETACH DELETE", s.log[-1])
    def test_undo_runs_even_if_query_fails(self):
        s = FakeSession(fail_on="MERGE"); st, _ = rq.run_one(s, q_by_id("Q20"), allow_writes=True)
        self.assertEqual(st, "FAIL"); self.assertIn("DETACH DELETE", s.log[-1])
    def test_expect_error_passes_only_on_error(self):
        q = q_by_id("Q19")
        self.assertEqual(rq.run_one(FakeSession(fail_on="CREATE"), q, True)[0], "PASS")
        self.assertEqual(rq.run_one(FakeSession(), q, True)[0], "FAIL")
    def test_skip_run(self): self.assertEqual(rq.run_one(FakeSession(), q_by_id("Q23"), True)[0], "SKIP")
    def test_read_query_multi_statement(self):
        s = FakeSession(); st, d = rq.run_one(s, q_by_id("Q02"), False); self.assertEqual(st, "PASS"); self.assertEqual(len(s.log), 2)

if __name__ == "__main__": unittest.main()
