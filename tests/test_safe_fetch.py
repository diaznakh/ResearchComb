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
    def __init__(self, status=200, body=b"paper", location=None, headers=None):
        self.status, self.body, self.location = status, body, location
        self.headers = {key.lower(): value for key, value in (headers or {}).items()}
        if location is not None:
            self.headers["location"] = location

    def getheader(self, name):
        return self.headers.get(name.lower())

    def read(self, count):
        chunk, self.body = self.body[:count], self.body[count:]
        return chunk


class Connection:
    responses = []
    pinned = []
    requests = []

    def __init__(self, host, port, **options):
        self.host, self.port = host, port
        self._create_connection = lambda address, timeout, source_address=None: None

    def request(self, method, target, headers):
        Connection.requests.append((method, target, dict(headers)))
        self._create_connection((self.host, self.port), 10)

    def getresponse(self):
        return self.responses.pop(0)

    def close(self):
        pass


class SafeFetchTests(unittest.TestCase):
    def setUp(self):
        self.old_env = {}
        for key in [
            "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
            "RESEARCHCOMB_CACHE", "RESEARCHCOMB_NO_CACHE", "RESEARCHCOMB_CACHE_DIR",
            "RESEARCHCOMB_CACHE_TTL", "RESEARCHCOMB_CACHE_MAX_BYTES",
        ]:
            self.old_env[key] = safe_fetch.os.environ.pop(key, None)
        Connection.requests = []
    
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
            with self.assertRaisesRegex(ValueError, "loopback|link-local"):
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
    
    def test_proxy_with_tunnel_uses_https_connection_for_https_targets(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]):
            output = Path(directory) / "paper.pdf"
            safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
            
            tunnel_called = []
            connection_class_used = []
            
            class HTTPSConn:
                def __init__(self, host, port, timeout=None, context=None):
                    self.host, self.port = host, port
                    connection_class_used.append("HTTPSConnection")
                def request(self, method, target, headers):
                    pass
                def getresponse(self):
                    return Response()
                def close(self):
                    pass
                def set_tunnel(self, host, port):
                    tunnel_called.append((self.host, self.port, host, port))
            
            class HTTPConn:
                def __init__(self, host, port, timeout=None):
                    self.host, self.port = host, port
                    connection_class_used.append("HTTPConnection")
                def request(self, method, target, headers):
                    pass
                def getresponse(self):
                    return Response()
                def close(self):
                    pass
                def set_tunnel(self, host, port):
                    tunnel_called.append((self.host, self.port, host, port))
            
            with patch.object(safe_fetch.http.client, "HTTPConnection", HTTPConn), \
                 patch.object(safe_fetch.http.client, "HTTPSConnection", HTTPSConn):
                safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
                self.assertEqual(output.read_bytes(), b"paper")
                # Verify HTTPSConnection was used for HTTPS target even with HTTP proxy
                self.assertEqual(connection_class_used, ["HTTPSConnection"])
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

    def test_proxy_env_without_opt_in_blocks_private_destinations(self):
        safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "paper.pdf"
            
            # Private DNS should be blocked even with proxy env set
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 443))]):
                with self.assertRaisesRegex(ValueError, "private|non-global"):
                    safe_fetch.fetch("https://internal.example.org/", output)
            
            # Link-local addresses should be blocked
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 443))]):
                with self.assertRaisesRegex(ValueError, "loopback|link-local"):
                    safe_fetch.fetch("https://metadata.example.org/", output)
    
    def test_proxy_env_with_no_proxy_wildcard_still_blocks_private(self):
        safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
        safe_fetch.os.environ["NO_PROXY"] = "*"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "paper.pdf"
            
            # Loopback should be blocked even when NO_PROXY bypasses the proxy
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 443))]):
                with self.assertRaisesRegex(ValueError, "loopback|link-local"):
                    safe_fetch.fetch("https://localhost.example.org/", output)
    
    def test_proxy_env_blocks_private_destinations_on_redirect(self):
        # Without allow_private, proxy is not used, so redirect to private address is blocked
        Connection.responses = [Response(302, location="https://internal.example.org/secret")]
        safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo") as dns, \
             patch.object(safe_fetch.socket, "create_connection"):
            output = Path(directory) / "paper.pdf"
            
            def resolve(host, port, *args, **kwargs):
                if host == "public.example.org":
                    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]
                elif host == "internal.example.org":
                    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 443))]
                return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]
            
            dns.side_effect = resolve
            with patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
                with self.assertRaisesRegex(ValueError, "private|non-global"):
                    safe_fetch.fetch("https://public.example.org/", output)
    
    def test_no_proxy_supports_wildcard_in_list(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            safe_fetch.os.environ["HTTPS_PROXY"] = "http://proxy.example.org:8080"
            safe_fetch.os.environ["NO_PROXY"] = "other.org, *, more.org"
            Connection.responses = [Response()]
            safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
            self.assertEqual(output.read_bytes(), b"paper")
    
    def test_loopback_blocked_even_in_allow_private_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "paper.pdf"
            
            # Test IPv4 loopback
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 443))]):
                with self.assertRaisesRegex(ValueError, "loopback"):
                    safe_fetch.fetch("https://localhost-alias.example.org/", output, allow_private=True)
            
            # Test IPv6 loopback
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::1", 443))]):
                with self.assertRaisesRegex(ValueError, "loopback"):
                    safe_fetch.fetch("https://localhost-alias.example.org/", output, allow_private=True)
            
            # Test link-local IPv4 (169.254.x.x)
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 443))]):
                with self.assertRaisesRegex(ValueError, "link-local"):
                    safe_fetch.fetch("https://metadata.example.org/", output, allow_private=True)
            
            # Test link-local IPv6 (fe80::/10)
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("fe80::1", 443))]):
                with self.assertRaisesRegex(ValueError, "link-local"):
                    safe_fetch.fetch("https://local.example.org/", output, allow_private=True)
            
            # Test unspecified IPv4 (0.0.0.0/8 - connects to localhost on Linux)
            for test_ip in ["0.0.0.0", "0.1.2.3"]:
                with self.subTest(ip=test_ip):
                    with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", (test_ip, 443))]):
                        with self.assertRaisesRegex(ValueError, "unspecified"):
                            safe_fetch.fetch("https://zero.example.org/", output, allow_private=True)
            
            # Test unspecified IPv6 (::)
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::", 443))]):
                with self.assertRaisesRegex(ValueError, "unspecified"):
                    safe_fetch.fetch("https://zero.example.org/", output, allow_private=True)
    
    def test_https_proxy_url_rejected(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))]):
            output = Path(directory) / "paper.pdf"
            safe_fetch.os.environ["HTTPS_PROXY"] = "https://proxy.example.org:8080"
            with self.assertRaisesRegex(ValueError, "https:// proxy URLs are not supported"):
                safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
    
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

    def test_dns_rebinding_prevented_in_allow_private_mode(self):
        Connection.responses = [Response()]
        public = (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(safe_fetch.socket, "getaddrinfo", return_value=[public]), \
             patch.object(safe_fetch.socket, "create_connection") as connect, \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            output = Path(directory) / "paper.pdf"
            safe_fetch.fetch("https://paper.example.org/study", output, allow_private=True)
            # Verify connection used validated IP, not hostname (prevents DNS rebinding)
            self.assertEqual(connect.call_args.args[0], ("93.184.216.34", 443))

    def _cached_fetch(self, directory, url, output, **kwargs):
        safe_fetch.os.environ["RESEARCHCOMB_CACHE_DIR"] = str(Path(directory) / "cache")
        public = (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 443))
        with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[public]), \
             patch.object(safe_fetch.socket, "create_connection"), \
             patch.object(safe_fetch.http.client, "HTTPSConnection", Connection):
            return safe_fetch.fetch(url, output, **kwargs)

    def test_cache_hit_skips_second_network_call(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "one.pdf", Path(directory) / "two.pdf"
            Connection.responses = [Response()]
            self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
            self._cached_fetch(directory, "https://paper.example.org/study", second, use_cache=True)
            self.assertEqual(len(Connection.requests), 1)
            self.assertEqual(first.read_bytes(), b"paper")
            self.assertEqual(second.read_bytes(), b"paper")

    def test_cache_hit_copies_into_fresh_output_not_shared_file(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "one.pdf", Path(directory) / "two.pdf"
            Connection.responses = [Response()]
            self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
            self._cached_fetch(directory, "https://paper.example.org/study", second, use_cache=True)
            cache_bodies = list((Path(directory) / "cache").glob("*.bin"))
            self.assertEqual(len(cache_bodies), 1)
            self.assertEqual(len({first.resolve(), second.resolve(), cache_bodies[0].resolve()}), 3)
            first.write_bytes(b"mutated")
            self.assertEqual(second.read_bytes(), b"paper")
            self.assertEqual(cache_bodies[0].read_bytes(), b"paper")
            self.assertFalse(first.is_symlink() or second.is_symlink() or cache_bodies[0].samefile(second))

    def test_cache_keyed_by_final_url_after_redirect(self):
        with tempfile.TemporaryDirectory() as directory:
            first, cached_final, original_again = Path(directory) / "a.pdf", Path(directory) / "b.pdf", Path(directory) / "c.pdf"
            Connection.responses = [Response(302, location="https://paper.example.org/final"), Response(body=b"final-body")]
            self._cached_fetch(directory, "https://paper.example.org/start", first, use_cache=True)
            self.assertEqual(first.read_bytes(), b"final-body")
            self.assertEqual(len(Connection.requests), 2)
            self._cached_fetch(directory, "https://paper.example.org/final", cached_final, use_cache=True)
            self.assertEqual(len(Connection.requests), 2)
            self.assertEqual(cached_final.read_bytes(), b"final-body")
            Connection.responses = [Response(404)]
            with self.assertRaisesRegex(ValueError, "HTTP 404"):
                self._cached_fetch(directory, "https://paper.example.org/start", original_again, use_cache=True)
            self.assertEqual(len(Connection.requests), 3)

    def test_cache_ttl_expiry_refetches(self):
        with tempfile.TemporaryDirectory() as directory:
            safe_fetch.os.environ["RESEARCHCOMB_CACHE_TTL"] = "10"
            first, second, third = Path(directory) / "a.pdf", Path(directory) / "b.pdf", Path(directory) / "c.pdf"
            clock = {"now": 1_000.0}
            Connection.responses = [Response(), Response(body=b"fresh")]
            with patch.object(safe_fetch.time, "time", side_effect=lambda: clock["now"]):
                self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
                clock["now"] = 1_009.0
                self._cached_fetch(directory, "https://paper.example.org/study", second, use_cache=True)
                self.assertEqual(len(Connection.requests), 1)
                self.assertEqual(second.read_bytes(), b"paper")
                clock["now"] = 1_011.0
                self._cached_fetch(directory, "https://paper.example.org/study", third, use_cache=True)
            self.assertEqual(len(Connection.requests), 2)
            self.assertEqual(third.read_bytes(), b"fresh")

    def test_errors_and_429_are_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            failed, ok, cached = Path(directory) / "fail.pdf", Path(directory) / "ok.pdf", Path(directory) / "hit.pdf"
            Connection.responses = [Response(429), Response(404)]
            with self.assertRaisesRegex(ValueError, "HTTP 429"):
                self._cached_fetch(directory, "https://paper.example.org/limited", failed, use_cache=True)
            with self.assertRaisesRegex(ValueError, "HTTP 404"):
                self._cached_fetch(directory, "https://paper.example.org/missing", failed, use_cache=True)
            self.assertFalse(failed.exists())
            Connection.responses = [Response(), Response()]
            self._cached_fetch(directory, "https://paper.example.org/limited", ok, use_cache=True)
            self._cached_fetch(directory, "https://paper.example.org/missing", Path(directory) / "missing-ok.pdf", use_cache=True)
            requests_after_store = len(Connection.requests)
            self._cached_fetch(directory, "https://paper.example.org/limited", cached, use_cache=True)
            self.assertEqual(len(Connection.requests), requests_after_store)
            self.assertEqual(cached.read_bytes(), b"paper")

    def test_cache_control_no_store_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.pdf", Path(directory) / "b.pdf"
            Connection.responses = [
                Response(headers={"Cache-Control": "max-age=60, no-store"}),
                Response(headers={"Cache-Control": "no-store"}),
            ]
            self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
            self._cached_fetch(directory, "https://paper.example.org/study", second, use_cache=True)
            self.assertEqual(len(Connection.requests), 2)

    def test_no_cache_flag_and_env_disable(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second, third = Path(directory) / "a.pdf", Path(directory) / "b.pdf", Path(directory) / "c.pdf"
            Connection.responses = [Response(), Response(), Response()]
            self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
            self._cached_fetch(directory, "https://paper.example.org/study", second, use_cache=True, no_cache=True)
            self.assertEqual(len(Connection.requests), 2)
            safe_fetch.os.environ["RESEARCHCOMB_NO_CACHE"] = "1"
            self._cached_fetch(directory, "https://paper.example.org/study", third, use_cache=True)
            self.assertEqual(len(Connection.requests), 3)

    def test_cache_opt_in_default_off(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.pdf", Path(directory) / "b.pdf"
            Connection.responses = [Response(), Response()]
            self._cached_fetch(directory, "https://paper.example.org/study", first)
            self._cached_fetch(directory, "https://paper.example.org/study", second)
            self.assertEqual(len(Connection.requests), 2)

    def test_cache_hit_still_validates_dns(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.pdf", Path(directory) / "b.pdf"
            Connection.responses = [Response()]
            self._cached_fetch(directory, "https://paper.example.org/study", first, use_cache=True)
            safe_fetch.os.environ["RESEARCHCOMB_CACHE_DIR"] = str(Path(directory) / "cache")
            with patch.object(safe_fetch.socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.2", 443))]):
                with self.assertRaisesRegex(ValueError, "private"):
                    safe_fetch.fetch("https://paper.example.org/study", second, use_cache=True)
            self.assertFalse(second.exists())


if __name__ == "__main__":
    unittest.main()
