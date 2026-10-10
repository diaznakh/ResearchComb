"""Fetch a public research URL without connecting to private network addresses."""

import http.client
import ipaddress
import os
import re
import socket
import ssl
import sys
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

MAX_BYTES = 20 * 1024 * 1024
MAX_REDIRECTS = 5


def public_endpoint(url, allow_private=False):
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
    if not addresses:
        raise ValueError("no addresses resolved")
    if not allow_private and any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("private or non-global DNS destination is blocked")
    return parsed, sorted(addresses)[0], port


def in_no_proxy(hostname, no_proxy):
    if no_proxy == "*":
        return True
    hostname = hostname.lower()
    for entry in no_proxy.split(","):
        entry = entry.strip().lower()
        if entry == hostname or entry.startswith(".") and hostname.endswith(entry):
            return True
        if hostname == entry.lstrip(".") or hostname.endswith("." + entry.lstrip(".")):
            return True
    return False


def is_stub_or_challenge(body):
    if len(body) > 10240:
        return False
    text = body.lower()
    if b"http-equiv" in text and b"refresh" in text:
        match = re.search(rb'http-equiv\s*=\s*["\']?\s*refresh\s*["\']?\s+content\s*=\s*["\']?(\d+)', text, re.I)
        if match and int(match.group(1)) < 5:
            return True
    if b"enable cookies" in text and b"pubmed.ncbi.nlm.nih.gov" in text:
        return True
    return False


def fetch(url, output, allow_private=False, overwrite=False):
    proxy_url = os.environ.get("HTTPS_PROXY", os.environ.get("HTTP_PROXY")) or \
                os.environ.get("https_proxy", os.environ.get("http_proxy"))
    no_proxy = os.environ.get("NO_PROXY", os.environ.get("no_proxy", ""))
    
    for _ in range(MAX_REDIRECTS + 1):
        parsed, ip, port = public_endpoint(url, allow_private or bool(proxy_url))
        use_proxy = proxy_url and not in_no_proxy(parsed.hostname, no_proxy)
        
        if use_proxy:
            proxy_parsed = urlsplit(proxy_url if "://" in proxy_url else f"http://{proxy_url}")
            if proxy_parsed.scheme not in {"http", "https"}:
                raise ValueError("proxy URL must be HTTP or HTTPS")
            proxy_port = proxy_parsed.port or (8080 if proxy_parsed.scheme == "http" else 443)
            
            if parsed.scheme == "https":
                if proxy_parsed.scheme == "https":
                    connection = http.client.HTTPSConnection(proxy_parsed.hostname, proxy_port, timeout=10)
                else:
                    connection = http.client.HTTPConnection(proxy_parsed.hostname, proxy_port, timeout=10)
                connection.set_tunnel(parsed.hostname, port)
            else:
                if proxy_parsed.scheme == "https":
                    connection = http.client.HTTPSConnection(proxy_parsed.hostname, proxy_port, timeout=10)
                else:
                    connection = http.client.HTTPConnection(proxy_parsed.hostname, proxy_port, timeout=10)
                connection.set_tunnel(parsed.hostname, port)
            target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        else:
            cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
            options = {"timeout": 10}
            if parsed.scheme == "https":
                options["context"] = ssl.create_default_context()
            connection = cls(parsed.hostname, port, **options)
            if not allow_private:
                connection._create_connection = lambda address, timeout, source_address=None: socket.create_connection(
                    (ip, port), timeout, source_address
                )
            target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        
        try:
            connection.request("GET", target, headers={"Connection": "close", "User-Agent": "ResearchComb/0.5.23 (+https://github.com/diaznakh/ResearchComb)"})
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("redirect has no destination")
                url = urljoin(url, location)
                continue
            if not (200 <= response.status < 207 and response.status not in {204, 205}):
                raise ValueError(f"HTTP {response.status}")
            size = 0
            body = b""
            temp_path = None
            created = False
            try:
                if overwrite:
                    fd, temp_path = tempfile.mkstemp(dir=Path(output).parent, prefix=".safe_fetch_")
                    destination = os.fdopen(fd, "wb")
                    created = True
                else:
                    destination = Path(output).open("xb")
                    created = True
                
                while chunk := response.read(min(65536, MAX_BYTES - size + 1)):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError("source exceeds 20 MiB limit")
                    body += chunk
                    destination.write(chunk)
                destination.close()
                
                if is_stub_or_challenge(body):
                    raise ValueError("received redirect stub or challenge page instead of content")
                
                if temp_path:
                    Path(temp_path).replace(output)
                    temp_path = None
                
                return url, size
            except BaseException:
                if created:
                    if temp_path and Path(temp_path).exists():
                        Path(temp_path).unlink()
                    elif not overwrite and Path(output).exists():
                        Path(output).unlink(missing_ok=True)
                raise
        finally:
            connection.close()
    raise ValueError("too many redirects")


if __name__ == "__main__":
    try:
        allow_private = os.environ.get("RESEARCHCOMB_ALLOW_PRIVATE") == "1"
        args = sys.argv[1:]
        overwrite = False
        
        while args and args[0].startswith("--"):
            if args[0] == "--allow-private":
                allow_private = True
                args = args[1:]
            elif args[0] == "--overwrite":
                overwrite = True
                args = args[1:]
            else:
                raise ValueError(f"unknown option: {args[0]}")
        
        if len(args) != 2:
            raise ValueError("usage: safe_fetch.py [--allow-private] [--overwrite] URL OUTPUT_FILE")
        
        final_url, size = fetch(args[0], args[1], allow_private, overwrite)
        mode = " (private addresses allowed)" if allow_private else ""
        print(f"Saved {size} bytes from {final_url} to {args[1]}{mode}")
    except (OSError, ValueError, http.client.HTTPException) as error:
        sys.exit(f"FAIL: {error}")
