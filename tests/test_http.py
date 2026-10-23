import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from app import Handler
from mcwindow.demo import demo


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def call(self, path, data=None, extra=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Content-Type":"application/json"}
        headers.update(extra or {})
        connection.request("POST" if data is not None else "GET", path,
                           json.dumps(data).encode() if data is not None else None, headers)
        response = connection.getresponse()
        status, headers, body = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return status, headers, body

    def test_app_and_static_assets(self):
        for path in ["/", "/app.js", "/style.css", "/mark.svg"]:
            with self.subTest(path=path):
                status, headers, body = self.call(path)
                self.assertEqual(status, 200)
                self.assertGreater(len(body), 30)
                self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_plan_and_exports(self):
        status, _, body = self.call("/api/plan", demo())
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["recommendation"]["price_fen"], 1990)
        for path, expected in [("calendar", b'BEGIN:VCALENDAR'), ("report", '# 麦麦空档'.encode())]:
            status, headers, body = self.call("/api/"+path, demo())
            self.assertEqual(status, 200)
            self.assertIn("attachment", headers["Content-Disposition"])
            self.assertIn(expected, body)

    def test_invalid_input_is_400(self):
        self.assertEqual(self.call("/api/plan", {})[0], 400)
        self.assertEqual(self.call("/api/plan", [1,2])[0], 400)

    def test_origin_and_host_checks(self):
        self.assertEqual(self.call("/api/plan", demo(), {"Origin":"https://external.example"})[0], 403)
        self.assertEqual(self.call("/api/health", extra={"Host":"external.example"})[0], 403)

    def test_paths_do_not_expose_source_or_secrets(self):
        for path in ["/../app.py", "/.env", "/mcwindow/mcp_client.py"]:
            self.assertEqual(self.call(path)[0], 404)


if __name__ == "__main__":
    unittest.main()
