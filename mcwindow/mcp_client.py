"""Small, bounded Streamable HTTP MCP client; no tokens or raw payloads logged."""
import json
import socket
from urllib import request, error

ENDPOINT = "https://mcp.mcd.cn"
ALLOWED_TOOLS = frozenset({"campaign-calendar", "available-coupons", "query-my-coupons", "now-time-info"})
MAX_RESPONSE = 2 * 1024 * 1024


class MCPError(RuntimeError):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise MCPError("官方服务返回了重定向；为避免凭证转发，已停止连接。")


def decode_response(raw, content_type, expected_id):
    if "text/event-stream" in content_type:
        # SSE may contain progress, keep-alives, multiline data, and several events.
        blocks = raw.decode("utf-8-sig").replace("\r\n", "\n").split("\n\n")
        for block in blocks:
            data = "\n".join(line[5:].lstrip(" ") for line in block.splitlines() if line.startswith("data:"))
            if not data:
                continue
            try:
                value = json.loads(data)
            except ValueError:
                continue
            if isinstance(value, dict) and value.get("id") == expected_id:
                return value
        raise MCPError("SSE 中没有匹配的 MCP 响应。")
    try:
        value = json.loads(raw)
    except ValueError:
        raise MCPError("MCP 返回了无法解析的 JSON。")
    if not isinstance(value, dict) or value.get("id") != expected_id:
        raise MCPError("MCP 响应编号不匹配。")
    return value


class Client:
    def __init__(self, token, timeout=18):
        if not isinstance(token, str) or not token.strip() or len(token) > 4096 or any(c.isspace() for c in token.strip()):
            raise MCPError("请在本机输入有效的 MCP Token。")
        self.token, self.timeout = token.strip(), timeout
        self.session, self.protocol, self.counter = None, "2025-03-26", 0
        self.opener = request.build_opener(NoRedirect)

    def _post(self, method, params=None, notification=False):
        self.counter += 1
        rid = self.counter
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if not notification:
            payload["id"] = rid
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "Authorization": "Bearer " + self.token}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        if method != "initialize":
            headers["MCP-Protocol-Version"] = self.protocol
        req = request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                if response.headers.get("Mcp-Session-Id"):
                    self.session = response.headers["Mcp-Session-Id"]
                if notification:
                    return None
                content_type = response.headers.get("Content-Type", "")
                if "text/event-stream" in content_type:
                    # Do not read to EOF: a Streamable HTTP connection can stay open.
                    chunks, size = [], 0
                    while True:
                        line = response.readline(MAX_RESPONSE + 1)
                        if not line:
                            break
                        chunks.append(line)
                        size += len(line)
                        if size > MAX_RESPONSE:
                            raise MCPError("响应超过2MB，已停止读取。")
                        if line.strip() == b"":
                            try:
                                value = decode_response(b"".join(chunks), content_type, rid)
                                break
                            except MCPError:
                                continue
                    else:
                        value = None
                    if not chunks:
                        raise MCPError("官方服务返回了空响应。")
                    value = decode_response(b"".join(chunks), content_type, rid)
                else:
                    raw = response.read(MAX_RESPONSE + 1)
                    if len(raw) > MAX_RESPONSE:
                        raise MCPError("响应超过2MB，已停止读取。")
                    value = decode_response(raw, content_type, rid)
        except error.HTTPError as exc:
            messages = {401: "Token 无效或已过期，请重新申请。", 403: "当前账户无权访问该服务。", 429: "请求过于频繁，请稍后再试。"}
            raise MCPError(messages.get(exc.code, "官方服务 HTTP 错误 %d。" % exc.code)) from None
        except (error.URLError, socket.timeout, TimeoutError, OSError):
            raise MCPError("连接官方服务超时或失败，请检查网络后重试。") from None
        if "error" in value:
            # Never echo an uncontrolled upstream error containing account information.
            raise MCPError("MCP 返回调用错误，请检查工具参数或 Token 权限。")
        if not isinstance(value.get("result"), dict):
            raise MCPError("MCP 结果格式不符合预期。")
        return value["result"]

    def initialize(self):
        info = self._post("initialize", {"protocolVersion": self.protocol, "capabilities": {},
                                          "clientInfo": {"name": "mcwindow", "version": "1.0.0"}})
        version = info.get("protocolVersion")
        if version:
            self.protocol = str(version)
        self._post("notifications/initialized", notification=True)
        return info

    def tools(self):
        result, cursor, seen = [], None, set()
        for _ in range(10):
            page = self._post("tools/list", {"cursor": cursor} if cursor else {})
            items = page.get("tools", [])
            if not isinstance(items, list):
                raise MCPError("工具列表格式异常。")
            result.extend(x for x in items if isinstance(x, dict) and x.get("name") in ALLOWED_TOOLS)
            cursor = page.get("nextCursor")
            if not cursor:
                return result
            if cursor in seen:
                break
            seen.add(cursor)
        raise MCPError("工具列表分页异常或页数过多。")

    def call(self, name, arguments):
        if name not in ALLOWED_TOOLS:
            raise MCPError("此项目只开放4个查询工具。")
        if not isinstance(arguments, dict):
            raise MCPError("工具参数须为 JSON 对象。")
        result = self._post("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise MCPError("工具执行未成功，请对照实时参数说明检查输入。")
        business = result.get("structuredContent")
        if isinstance(business, dict) and business.get("success") is False:
            raise MCPError("官方工具返回业务失败，请核对参数和账户条件后重试。")
        return result
