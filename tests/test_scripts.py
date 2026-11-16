"""Exercise the public launchers with disposable files and local HTTP only."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
COMMANDS = (
    "disk-usage", "clean-tmp", "clean-build", "reset-project", "json-pretty", "slugify",
    "new-project", "daily-routine", "csv-to-json", "organize-downloads", "download-assets",
    "api-health-check",
)


class CommandTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dot scripts ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def command(self, name, *args, stdin=None, code=0):
        result = subprocess.run(
            [str(REPO / "bin" / name), *map(str, args)], cwd=self.root,
            input=stdin, text=True, capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def file(self, relative, content="data"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class ScriptsTest(CommandTestCase):
    def test_launchers_work_outside_repository(self):
        for name in COMMANDS:
            with self.subTest(command=name):
                result = self.command(name, "--help")
                self.assertIn("usage:", result.stdout)

    def test_json_pretty_and_safe_output(self):
        result = self.command("json-pretty", "--sort-keys", stdin='{"z":2,"a":"سلام"}')
        self.assertEqual(result.stdout, '{\n  "a": "سلام",\n  "z": 2\n}\n')
        source = self.file("data.json", '{"a":1}')
        self.command("json-pretty", source, "-o", source, code=1)
        self.assertEqual(source.read_text(), '{"a":1}')
        for text in ("{broken", "NaN", "Infinity"):
            with self.subTest(text=text):
                self.command("json-pretty", "-o", "bad.json", stdin=text, code=1)
                self.assertFalse((self.root / "bad.json").exists())
        self.command("json-pretty", source, "-o", "pretty.json")
        self.assertEqual(json.loads((self.root / "pretty.json").read_text()), {"a": 1})

    def test_slugify_unicode_ascii_and_empty(self):
        self.assertEqual(self.command("slugify", " Hello__World! ").stdout, "hello-world\n")
        self.assertEqual(self.command("slugify", stdin="سلام دنیا").stdout, "سلام-دنیا\n")
        self.assertEqual(self.command("slugify", "Café déjà vu", "--ascii").stdout, "cafe-deja-vu\n")
        self.command("slugify", "!!!", code=1)

    def test_disk_usage_totals_depth_and_symlinks(self):
        self.file("tree/big/nested/data", "x" * 100)
        self.file("tree/small/data", "x" * 10)
        self.file("tree/root-file", "x" * 5)
        outside = self.file("outside/data", "x" * 1000).parent
        (self.root / "tree" / "linked").symlink_to(outside, target_is_directory=True)
        (self.root / "tree" / "linked-file").symlink_to(outside / "data")
        result = self.command("disk-usage", "tree")
        self.assertIn("115.0 B", result.stdout)
        self.assertLess(result.stdout.index("big/"), result.stdout.index("small/"))
        self.assertNotIn("nested/", result.stdout)
        self.assertNotIn("linked", result.stdout)
        self.assertIn("big/nested/", self.command("disk-usage", "tree", "--depth", 2).stdout)
        self.command("disk-usage", "absent", code=1)

    def test_clean_build_preview_apply_and_protected_paths(self):
        generated = [self.file("project/dist/app.js"), self.file("project/packages/app/build/main")]
        kept = [self.file("project/src/index.js"), self.file("project/.git/build/keep"),
                self.file("project/node_modules/dependency/dist/keep"), self.file("outside/keep")]
        (self.root / "project" / "out").symlink_to(self.root / "outside", target_is_directory=True)
        self.command("clean-build", "project")
        self.assertTrue(all(path.exists() for path in generated))
        self.command("clean-build", "project", "--apply")
        self.assertTrue(all(not path.exists() for path in generated))
        self.assertTrue(all(path.exists() for path in kept))
        self.assertTrue((self.root / "project/out").is_symlink())

    def test_reset_project_keeps_source_and_lockfiles(self):
        generated = [self.file("project/node_modules/pkg/index.js"), self.file("project/.next/cache/file"),
                     self.file("project/packages/app/.cache/file")]
        kept = [self.file("project/package-lock.json", "{}"), self.file("project/src/index.js")]
        self.command("reset-project", "project", "--dry-run")
        self.assertTrue(all(path.exists() for path in generated))
        self.command("reset-project", "project", "--apply")
        self.assertTrue(all(not path.exists() for path in generated))
        self.assertTrue(all(path.exists() for path in kept))

    def test_clean_tmp_age_filter(self):
        old = self.file("cache/nested/old")
        fresh = self.file("cache/new")
        protected = self.file("cache/.git/old")
        outside = self.file("outside/old")
        timestamp = time.time() - 10 * 86400
        for path in (old, protected, outside):
            os.utime(path, (timestamp, timestamp))
        (self.root / "cache/linked").symlink_to(outside)
        self.command("clean-tmp", "cache")
        self.assertTrue(old.exists())
        self.command("clean-tmp", "cache", "--apply")
        self.assertFalse(old.exists())
        self.assertTrue(fresh.exists() and protected.exists() and outside.exists())
        self.assertTrue(old.parent.is_dir())
        self.command("clean-tmp", "cache", "--days", "nan", code=2)

    def test_mutating_commands_refuse_unsafe_roots(self):
        target = self.file("project/file").parent
        link = self.root / "linked"
        link.symlink_to(target, target_is_directory=True)
        for name in ("clean-tmp", "clean-build", "reset-project", "organize-downloads"):
            for path in (Path.home(), "/", link):
                with self.subTest(command=name, path=path):
                    self.command(name, path, code=1)

    def test_new_project_templates_and_existing_destination(self):
        self.command("new-project", "sample", "--dry-run")
        self.assertFalse((self.root / "sample").exists())
        self.command("new-project", "sample")
        result = subprocess.run([sys.executable, "main.py"], cwd=self.root / "sample", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Hello, world!\n")
        original = (self.root / "sample/main.py").read_text()
        self.command("new-project", "sample", code=1)
        self.assertEqual((self.root / "sample/main.py").read_text(), original)
        self.command("new-project", "Node_App", "--template", "node")
        package = json.loads((self.root / "Node_App/package.json").read_text())
        self.assertEqual(package["name"], "node-app")
        self.assertEqual(package["scripts"]["start"], "node index.js")
        self.command("new-project", "bad name", code=1)

    def routine(self, steps):
        return self.file("config/routine.json", json.dumps({"steps": steps}))

    def test_routine_preview_relative_cwd_and_literal_arguments(self):
        script = "from pathlib import Path; import sys; Path('result').write_text(sys.argv[1])"
        argument = "literal; $(touch injected)"
        config = self.routine([{"command": [sys.executable, "-c", script, argument]}])
        self.command("daily-routine", config)
        destination = config.parent / "result"
        self.assertFalse(destination.exists())
        self.command("daily-routine", config, "--apply")
        self.assertEqual(destination.read_text(), argument)
        self.assertFalse((config.parent / "injected").exists())

    def test_routine_fail_fast_keep_going_and_validation(self):
        steps = [{"command": [sys.executable, "-c", "raise SystemExit(7)"]},
                 {"command": [sys.executable, "-c", "from pathlib import Path; Path('ran').touch()"]}]
        config = self.routine(steps)
        self.command("daily-routine", config, "--apply", code=1)
        self.assertFalse((config.parent / "ran").exists())
        self.command("daily-routine", config, "--apply", "--keep-going", code=1)
        self.assertTrue((config.parent / "ran").exists())
        config = self.routine([steps[1], {"command": "not an argv array"}])
        (config.parent / "ran").unlink()
        self.command("daily-routine", config, "--apply", code=1)
        self.assertFalse((config.parent / "ran").exists())

    def test_routine_timeout(self):
        config = self.routine([{"command": [sys.executable, "-c", "import time; time.sleep(10)"]}])
        self.command("daily-routine", config, "--apply", "--timeout", "0.1", code=1)

    def test_csv_multiline_bom_and_strings(self):
        source = self.file("input.csv", '\ufeffname,note,age\nسلام,"hello,\nworld",30\n')
        result = self.command("csv-to-json", source)
        self.assertEqual(json.loads(result.stdout), [{"name": "سلام", "note": "hello,\nworld", "age": "30"}])
        result = self.command("csv-to-json", "--delimiter", ";", stdin="a;b\n1;\n")
        self.assertEqual(json.loads(result.stdout), [{"a": "1", "b": ""}])

    def test_csv_rejects_lossy_rows_and_preserves_output(self):
        for text in ("a,a\n1,2\n", "a,\n1,2\n", "a,b\n1\n", "a,b\n1,2,3\n", 'a,b\n"unterminated,2'):
            with self.subTest(text=text):
                self.command("csv-to-json", "-o", "bad.json", stdin=text, code=1)
                self.assertFalse((self.root / "bad.json").exists())
        source = self.file("rows.csv", "a\n1\n")
        self.command("csv-to-json", source, "-o", source, code=1)
        self.assertEqual(source.read_text(), "a\n1\n")

    def test_organize_downloads_preview_collisions_and_skips(self):
        original = self.file("inbox/images/photo.jpg", "existing")
        source = self.file("inbox/photo.jpg", "new")
        self.file("inbox/report.PDF", "report")
        self.file("inbox/unknown.xyz", "other")
        kept = [self.file("inbox/.hidden"), self.file("inbox/pending.part"), self.file("inbox/subdir/keep")]
        (self.root / "inbox/link").symlink_to(source)
        self.command("organize-downloads", "inbox")
        self.assertTrue(source.exists())
        self.assertFalse((self.root / "inbox/documents").exists())
        self.command("organize-downloads", "inbox", "--apply")
        self.assertEqual(original.read_text(), "existing")
        self.assertEqual((self.root / "inbox/images/photo-1.jpg").read_text(), "new")
        self.assertTrue((self.root / "inbox/documents/report.PDF").exists())
        self.assertTrue((self.root / "inbox/other/unknown.xyz").exists())
        self.assertTrue(all(path.exists() for path in kept))
        self.assertTrue((self.root / "inbox/link").is_symlink())

    def test_organize_downloads_refuses_category_symlink_before_moves(self):
        self.file("inbox/a.pdf")
        self.file("inbox/photo.jpg")
        (self.root / "outside").mkdir()
        (self.root / "inbox/images").symlink_to(self.root / "outside", target_is_directory=True)
        self.command("organize-downloads", "inbox", "--apply", code=1)
        self.assertTrue((self.root / "inbox/a.pdf").exists())
        self.assertFalse((self.root / "inbox/documents").exists())


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/slow":
            time.sleep(0.3)
        if self.path in {"/redirect", "/redirect-ftp"}:
            self.send_response(302)
            location = "ftp://127.0.0.1/asset.txt" if self.path == "/redirect-ftp" else "/asset.txt"
            self.send_header("Location", location)
            self.end_headers()
            return
        status = 503 if self.path == "/unhealthy" else 404 if self.path == "/missing" else 200
        payload = b"test asset\n"
        self.send_response(status)
        self.send_header("Content-Length", str(100 if self.path == "/truncated.txt" else len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass


class NetworkTest(CommandTestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health_status_json_expected_and_redirect(self):
        result = self.command("api-health-check", self.url + "/asset.txt", self.url + "/unhealthy", "--json", code=1)
        statuses = json.loads(result.stdout)
        self.assertEqual([item["status"] for item in statuses], [200, 503])
        self.assertEqual([item["ok"] for item in statuses], [True, False])
        self.command("api-health-check", self.url + "/missing", "--expect", "404")
        self.command("api-health-check", self.url + "/redirect")

    def test_health_timeout_and_invalid_inputs(self):
        result = self.command("api-health-check", self.url + "/slow", "--timeout", "0.05", "--json", code=1)
        self.assertIsNone(json.loads(result.stdout)[0]["status"])
        self.command("api-health-check", "file:///etc/hosts", code=1)
        self.command("api-health-check", "http://localhost:bad", code=1)
        self.command("api-health-check", self.url, "--workers", "0", code=2)

    def test_network_helpers_reject_non_http_redirects(self):
        result = self.command("api-health-check", self.url + "/redirect-ftp", "--json", code=1)
        self.assertEqual(json.loads(result.stdout)[0]["error"], "Redirect must use HTTP(S)")
        result = self.command("download-assets", self.url + "/redirect-ftp", code=1)
        self.assertIn("Redirect must use HTTP(S)", result.stderr)
        self.assertEqual(list((self.root / "assets").iterdir()), [])

    def test_health_url_file_and_unreachable(self):
        urls = self.file("urls.txt", f"# endpoints\n\n{self.url}/asset.txt\n")
        self.command("api-health-check", "-f", urls)
        # Bind a port without listening so refusal is local and deterministic.
        import socket
        with socket.socket() as unused:
            unused.bind(("127.0.0.1", 0))
            self.command("api-health-check", f"http://127.0.0.1:{unused.getsockname()[1]}/", code=1)

    def test_download_assets_files_and_existing_output(self):
        urls = self.file("urls.txt", f"# assets\n\n{self.url}/asset.txt?version=1\n")
        self.command("download-assets", "-f", urls, "-d", "my assets")
        target = self.root / "my assets/asset.txt"
        self.assertEqual(target.read_bytes(), b"test asset\n")
        self.command("download-assets", self.url + "/asset.txt", "-d", "my assets", code=1)
        self.assertEqual(target.read_bytes(), b"test asset\n")
        self.assertEqual([path.name for path in target.parent.iterdir()], ["asset.txt"])

    def test_download_failures_clean_partial_files_and_continue(self):
        self.command("download-assets", self.url + "/missing", self.url + "/truncated.txt",
                     self.url + "/asset.txt", "-d", "assets", code=1)
        self.assertEqual(sorted(path.name for path in (self.root / "assets").iterdir()), ["asset.txt"])

    def test_download_rejects_unsafe_names_duplicates_and_non_http(self):
        for urls in ([self.url + "/%2E%2E"], [self.url + "/a%2Fb"],
                     [self.url + "/asset.txt?a", self.url + "/asset.txt?b"], ["file:///etc/hosts"]):
            with self.subTest(urls=urls):
                self.command("download-assets", *urls, code=1)
                self.assertFalse((self.root / "assets").exists())


if __name__ == "__main__":
    unittest.main()
