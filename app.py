#!/usr/bin/env python3
"""Local-only app. Python 3.9+, no third-party dependencies."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
from urllib.parse import urlparse

from mcwindow.demo import demo
from mcwindow.engine import plan, calendar, report, ValidationError
from mcwindow.mcp_client import Client, MCPError

STATIC = Path(__file__).resolve().parent / "web"


class Handler(BaseHTTPRequestHandler):
    server_version = "McWindow/1.0"

    def log_message(self, fmt, *args):
        # Avoid logging submitted tokens, bodies and account responses.
        pass

    def trusted(self):
        allowed = {"localhost:%d" % self.server.server_port, "127.0.0.1:%d" % self.server.server_port}
        if self.headers.get("Host") not in allowed:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in {"http://" + host for host in allowed}

    def respond(self, status, payload, content_type="application/json; charset=utf-8", filename=None):
        body = json.dumps(payload, ensure_ascii=False).encode() if content_type.startswith("application/json") else payload
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if filename:
            self.send_header("Content-Disposition", 'attachment; filename="%s"' % filename)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.trusted():
            self.respond(403, {"error": "仅允许本机页面访问"})
            return
        path = urlparse(self.path).path
        if path == "/api/demo":
            self.respond(200, demo())
        elif path == "/api/health":
            self.respond(200, {"ok": True, "version": "1.0.0", "mode": "local"})
        elif path in ("/", "/index.html", "/app.js", "/style.css", "/mark.svg"):
            file = STATIC / ("index.html" if path == "/" else path.lstrip("/"))
            if not file.is_file():
                self.respond(404, {"error": "文件不存在"})
                return
            mime = mimetypes.guess_type(str(file))[0] or "application/octet-stream"
            self.respond(200, file.read_bytes(), mime + ("; charset=utf-8" if mime.startswith("text/") or mime == "application/javascript" else ""))
        else:
            self.respond(404, {"error": "路径不存在"})

    def do_POST(self):
        if not self.trusted():
            self.respond(403, {"error": "仅允许本机页面访问"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024 * 1024:
                raise ValidationError("请求大小须在1MB以内")
            if not self.headers.get("Content-Type", "").startswith("application/json"):
                raise ValidationError("仅接受 application/json")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValidationError("请求须为 JSON 对象")
            path = urlparse(self.path).path
            if path in ("/api/plan", "/api/calendar", "/api/report"):
                result = plan(data)
                if path == "/api/calendar":
                    self.respond(200, calendar(result, data.get("selected_id")), "text/calendar; charset=utf-8", "mcwindow.ics")
                elif path == "/api/report":
                    self.respond(200, report(result), "text/markdown; charset=utf-8", "mcwindow-plan.md")
                else:
                    self.respond(200, result)
            elif path in ("/api/mcp/tools", "/api/mcp/call"):
                client = Client(data.get("token"))
                client.initialize()
                if path == "/api/mcp/tools":
                    self.respond(200, {"tools": client.tools()})
                else:
                    name = data.get("name")
                    self.respond(200, {"tool": name, "result": client.call(name, data.get("arguments", {}))})
            else:
                self.respond(404, {"error": "路径不存在"})
        except (ValidationError, MCPError, ValueError, TypeError) as exc:
            self.respond(400, {"error": str(exc) if isinstance(exc, (ValidationError, MCPError)) else "请求数据格式错误"})
        except Exception:
            self.respond(500, {"error": "本机服务遇到异常，请重试；没有保存 Token 或账户响应。"})


def main():
    parser = argparse.ArgumentParser(description="麦麦空档 · 本机用餐时间规划")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("McWindow 已启动：http://127.0.0.1:%d" % server.server_port, flush=True)
    print("仅监听本机；按 Ctrl+C 停止。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
