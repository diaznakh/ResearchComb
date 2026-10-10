"""Fetch a public research URL without connecting to private network addresses."""

import http.client
import ipaddress
import socket
import ssl
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit


MAX_BYTES = 20 * 1024 * 1024
MAX_REDIRECTS = 5


def public_endpoint(url):
    parsed = urlsplit(url)
    host = parsed.hostname
    if parsed.scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        raise ValueError("only public HTTP(S) URLs without credentials are allowed")
    host = host.rstrip(".").lower()
    if "." not in host or host == "home.arpa" or host.endswith((".localhost", ".local", ".internal", ".home.arpa")):
        raise ValueError("local hostnames are blocked")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("IP literal URLs are blocked")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    addresses = {item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("private or non-global DNS destination is blocked")
    return parsed, sorted(addresses)[0], port


def fetch(url, output):
    for _ in range(MAX_REDIRECTS + 1):
        parsed, ip, port = public_endpoint(url)
        cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        options = {"timeout": 10}
        if parsed.scheme == "https":
            options["context"] = ssl.create_default_context()
        connection = cls(parsed.hostname, port, **options)
        # Pin the validated address so DNS cannot change between the check and connection.
        connection._create_connection = lambda address, timeout, source_address=None: socket.create_connection(
            (ip, port), timeout, source_address
        )
        try:
            target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
            connection.request("GET", target, headers={"Connection": "close", "User-Agent": "ResearchComb"})
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("redirect has no destination")
                url = urljoin(url, location)
                continue
            if response.status != 200:
                raise ValueError(f"HTTP {response.status}")
            size = 0
            created = False
            try:
                with Path(output).open("xb") as destination:
                    created = True
                    while chunk := response.read(min(65536, MAX_BYTES - size + 1)):
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise ValueError("source exceeds 20 MiB limit")
                        destination.write(chunk)
            except BaseException:
                if created:
                    Path(output).unlink(missing_ok=True)
                raise
            return url, size
        finally:
            connection.close()
    raise ValueError("too many redirects")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise ValueError("usage: safe_fetch.py URL OUTPUT_FILE")
        final_url, size = fetch(sys.argv[1], sys.argv[2])
        print(f"Saved {size} bytes from {final_url} to {sys.argv[2]}")
    except (OSError, ValueError, http.client.HTTPException) as error:
        sys.exit(f"FAIL: {error}")
