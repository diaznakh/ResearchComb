"""Security checks for public research-link retrieval."""

import importlib.util
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/researchcomb/scripts/safe_fetch.py"
spec = importlib.util.spec_from_file_location("safe_fetch", SCRIPT)
safe_fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safe_fetch)


class Response:
    def __init__(self, status=200, body=b"paper", location=None):
        self.status, self.body, self.location = status, body, location

    def getheader(self, name):
        return self.location if name == "Location" else None

    def read(self, count):
        chunk, self.body = self.body[:count], self.body[count:]
        return chunk


class Connection:
    responses = []
    pinned = []

    def __init__(self, host, port, **options):
        self.host, self.port = host, port
        self._create_connection = lambda address, timeout, source_address=None: None

    def request(self, method, target, headers):
        self._create_connection((self.host, self.port), 10)

    def getresponse(self):
        return self.responses.pop(0)

    def close(self):
        pass


class SafeFetchTests(unittest.TestCase):
    def setUp(self):
        self.old_env = {}
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"]:
            self.old_env[key] = safe_fetch.os.environ.pop(key, None)
    
    def tearDown(self):
        for key, value in self.old_env.items():
            if value is not None:
                safe_fetch.os.environ[key] = value
            else:
                safe_fetch.os.environ.pop(key, None)
    
    def test_local_and_private_dns_are_rejected(self):
        for url in ("http://127.0.0.1/private", "http://localhost/private", "file:///etc/passwd", "https://user:pass@paper.example.org/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                safe_fetch.public_endpoint(url)
        with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 443))]):
            with self.assertRaisesRegex(ValueError, "private"):
                safe_fetch.public_endpoint("https://paper.example.org/")

    def test_public_fetch_pins_checked_address(self):
        Connection.responses = [Response()]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]) as dns, \
             patch.object(safe_fetch.socket, "create_connection") as connect, \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            self.assertEqual(safe_fetch.fetch("https://paper.example.org/study", output), ("https://paper.example.org/study", 5))
            self.assertEqual(output.read_bytes(), b"paper")
            self.assertEqual(connect.call_args.args[0], ("93.184.216.34", 443))
            self.assertEqual(dns.call_count, 1)

    def test_unsafe_redirect_and_existing_file_never_get_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            Connection.responses = [Response(302, location="http://127.0.0.1/private")]
            with self.assertRaisesRegex(ValueError, "IP literal"):
                safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertFalse(output.exists())
            output.write_bytes(b"keep")
            Connection.responses = [Response()]
            with self.assertRaises(FileExistsError):
                safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertEqual(output.read_bytes(), b"keep")
            Connection.responses = [Response()]
            safe_fetch.fetch("https://paper.example.org/study", output, overwrite=True)
            self.assertEqual(output.read_bytes(), b"paper")

    def test_redirect_dns_and_size_limit_fail_closed(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))
        private = (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.2", 443))
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            Connection.responses = [Response(302, location="https://other.example.org/private")]
            with patch.object(safe_fetch.socket, "getaddrinfo", side_effect=[[public], [private]]):
                with self.assertRaisesRegex(ValueError, "private"):
                    safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertFalse(output.exists())
            Connection.responses = [Response(body=b"123456")]
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[public]), \
                 patch.object(safe_fetch, "MAX_BYTES", 5):
                with self.assertRaisesRegex(ValueError, "limit"):
                    safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertFalse(output.exists())
    
    def test_http_2xx_responses_accepted(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            for status in (200, 201, 202, 203, 206):
                with self.subTest(status=status):
                    Connection.responses = [Response(status)]
                    safe_fetch.fetch("https://paper.example.org/study", output, overwrite=True)
                    self.assertEqual(output.read_bytes(), b"paper")
            for status in (204, 205, 400, 404, 500):
                with self.subTest(status=status):
                    Connection.responses = [Response(status)]
                    with self.assertRaisesRegex(ValueError, f"HTTP {status}"):
                        safe_fetch.fetch("https://paper.example.org/study", output, overwrite=True)
    
    def test_redirect_stub_detected(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            Connection.responses = [Response(body=b'<html><head><meta http-equiv="refresh" content="0;url=https://example.org/"></head></html>')]
            with self.assertRaisesRegex(ValueError, "stub"):
                safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertFalse(output.exists())
    
    def test_proxy_with_tunnel(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]):
            output = Path(directory) / "paper.pdf"
            safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
            
            tunnel_called = []
            
            class HTTPSConn:
                def __init__(self, host, port, timeout):
                    self.host, self.port = host, port
                def request(self, method, target, headers):
                    pass
                def getresponse(self):
                    return Response()
                def close(self):
                    pass
                def set_tunnel(self, host, port):
                    tunnel_called.append((self.host, self.port, host, port))
            
            class HTTPConn(HTTPSConn):
                pass
            
            with patch.object(safe_fetch.http.client, "HTTPConnection", HTTPConn), \
                 patch.object(safe_fetch.http.client, "HTTPSConnection", HTTPSConn):
                safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
                self.assertEqual(output.read_bytes(), b"paper")
                # Verify HTTPConnection was used for HTTP proxy and set_tunnel was called with target
                self.assertEqual(len(tunnel_called), 1)
                proxy_host, proxy_port, target_host, target_port = tunnel_called[0]
                self.assertEqual(proxy_host, "proxy.example.org")
                self.assertEqual(proxy_port, 8080)
                self.assertEqual(target_host, "paper.example.org")
                self.assertEqual(target_port, 443)
    
    def test_no_proxy_honored(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
            safe_fetch.os.environ["NO_PROXY"] = "paper.example.org"
            Connection.responses = [Response()]
            safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertEqual(output.read_bytes(), b"paper")

    def test_allow_private_mode_accepts_sandbox_addresses(self):
        Connection.responses = [Response()]
        benchmark = (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("198.18.0.1", 443))
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[benchmark]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            with self.assertRaisesRegex(ValueError, "private"):
                safe_fetch.fetch("https://paper.example.org/study", output)
            self.assertFalse(output.exists())
            final_url, size = safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
            self.assertEqual(final_url, "https://paper.example.org/study")
            self.assertEqual(output.read_bytes(), b"paper")


if __name__ == "__main__":
    unittest.main()
