import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from mcwindow.mcp_client import Client, MCPError, decode_response, NoRedirect


class Response(io.BytesIO):
    def __init__(self, body, headers=None):
        super().__init__(body)
        self.headers = headers or {"Content-Type": "application/json"}


class ProtocolTests(unittest.TestCase):
    def test_json_and_sse_notifications_and_multiline(self):
        raw = b': ping\n\nevent: message\ndata: {"jsonrpc":"2.0","method":"notifications/progress"}\n\nevent: message\ndata: {"jsonrpc":"2.0",\ndata: "id":7,"result":{"ok":true}}\n\n'
        self.assertEqual(decode_response(raw, "text/event-stream", 7)["result"], {"ok": True})
        self.assertEqual(decode_response(b'{"id":1,"result":{}}', "application/json", 1)["result"], {})

    def test_mismatched_id_and_bad_json_rejected(self):
        for raw in [b'{}', b'not-json', b'{"id":2,"result":{}}']:
            with self.assertRaises(MCPError):
                decode_response(raw, "application/json", 1)

    def test_session_protocol_authorization_and_call_wire(self):
        client = Client("test-placeholder-not-a-token")
        sent = []
        responses = [Response(b'{"id":1,"result":{"protocolVersion":"2025-06-18"}}', {"Mcp-Session-Id":"session-1", "Content-Type":"application/json"}),
                     Response(b''), Response(b'{"id":3,"result":{"content":[{"type":"text","text":"ok"}]}}')]

        def open_request(req, timeout):
            sent.append(req)
            return responses.pop(0)

        with patch.object(client.opener, "open", side_effect=open_request):
            client.initialize()
            self.assertEqual(client.call("campaign-calendar", {}), {"content":[{"type":"text","text":"ok"}]})
        self.assertEqual(sent[0].get_header("Authorization"), "Bearer test-placeholder-not-a-token")
        self.assertEqual(sent[2].get_header("Mcp-session-id"), "session-1")
        self.assertEqual(sent[2].get_header("Mcp-protocol-version"), "2025-06-18")
        self.assertEqual(json.loads(sent[1].data)["method"], "notifications/initialized")
        self.assertNotIn("id", json.loads(sent[1].data))
        self.assertEqual(json.loads(sent[2].data)["params"], {"name":"campaign-calendar", "arguments":{}})

    def test_sse_read_finishes_before_connection_eof(self):
        class LiveResponse(Response):
            def read(self, *args):
                raise AssertionError("SSE must not read until EOF")
        client = Client("test-placeholder")
        data = b': heartbeat\n\ndata: {"id":1,"result":{"tools":[]}}\n\n'
        with patch.object(client.opener, "open", return_value=LiveResponse(data, {"Content-Type":"text/event-stream"})):
            self.assertEqual(client._post("tools/list", {}), {"tools":[]})

    def test_tools_pagination_and_allowlist(self):
        client = Client("test-placeholder")
        pages = [{"tools":[{"name":"create-order"}, {"name":"campaign-calendar"}], "nextCursor":"page2"},
                 {"tools":[{"name":"query-my-coupons"}]}]
        with patch.object(client, "_post", side_effect=pages) as post:
            self.assertEqual([x["name"] for x in client.tools()], ["campaign-calendar", "query-my-coupons"])
            self.assertEqual(post.call_args_list[1].args, ("tools/list", {"cursor":"page2"}))

    def test_mutating_tool_is_blocked_without_network(self):
        client = Client("test-placeholder")
        for name in ["create-order", "auto-bind-coupons", "draw-lottery", "mall-create-order"]:
            with self.assertRaises(MCPError):
                client.call(name, {})

    def test_auth_errors_do_not_echo_body_or_token(self):
        client = Client("test-placeholder-secret")
        error = HTTPError("https://mcp.mcd.cn", 401, "test-placeholder-secret", {}, io.BytesIO(b'private-account-info'))
        with patch.object(client.opener, "open", side_effect=error):
            with self.assertRaises(MCPError) as caught:
                client._post("tools/list", {})
        self.assertNotIn("secret", str(caught.exception))
        self.assertIn("Token", str(caught.exception))

    def test_redirects_and_empty_token_rejected(self):
        with self.assertRaises(MCPError):
            Client("")
        with self.assertRaises(MCPError):
            NoRedirect().redirect_request(None,None,302,"",{},"https://other.example")

    def test_business_failure_is_not_reported_as_success(self):
        client = Client("test-placeholder")
        response = {"isError": False, "structuredContent": {"success": False, "code": 400, "message": "private-account-detail"}}
        with patch.object(client, "_post", return_value=response):
            with self.assertRaises(MCPError) as caught:
                client.call("query-my-coupons", {"page":"1"})
        self.assertIn("业务失败", str(caught.exception))
        self.assertNotIn("private-account-detail", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
