"""Fetch a public research URL without connecting to private network addresses."""

import hashlib
import http.client
import ipaddress
import json
import os
import re
import socket
import ssl
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

MAX_BYTES = 20 * 1024 * 1024
MAX_REDIRECTS = 5
USER_AGENT = "ResearchComb/0.5.23 (+https://github.com/diaznakh/ResearchComb)"
DEFAULT_CACHE_TTL = 24 * 60 * 60
DEFAULT_CACHE_MAX_BYTES = 64 * 1024 * 1024


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
    
    for ip_str in addresses:
        ip = ipaddress.ip_address(ip_str)
        # Block loopback, link-local, and full 0.0.0.0/8 range (including 0.1.2.3, etc.)
        if ip.is_loopback or ip.is_link_local or ip.is_unspecified or (isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network("0.0.0.0/8")):
            raise ValueError("loopback, link-local, and unspecified addresses are blocked")
        if not allow_private and not ip.is_global:
            raise ValueError("private or non-global DNS destination is blocked")
    
    return parsed, sorted(addresses)[0], port


def in_no_proxy(hostname, no_proxy):
    hostname = hostname.lower()
    for entry in no_proxy.split(","):
        entry = entry.strip().lower()
        if entry == "*":
            return True
        if entry == hostname or entry.startswith(".") and hostname.endswith(entry):
            return True
        if hostname == entry.lstrip(".") or hostname.endswith("." + entry.lstrip(".")):
            return True
    return False


def cache_enabled(use_cache=None, no_cache=False, allow_private=False):
    if allow_private or no_cache or os.environ.get("RESEARCHCOMB_NO_CACHE") == "1":
        return False
    if use_cache is True:
        return True
    if use_cache is False:
        return False
    return os.environ.get("RESEARCHCOMB_CACHE") == "1"


def cache_ttl():
    raw = os.environ.get("RESEARCHCOMB_CACHE_TTL")
    if not raw:
        return DEFAULT_CACHE_TTL
    value = int(raw)
    if value < 0:
        raise ValueError("cache TTL must be nonnegative")
    return value


def cache_max_bytes():
    raw = os.environ.get("RESEARCHCOMB_CACHE_MAX_BYTES")
    if not raw:
        return DEFAULT_CACHE_MAX_BYTES
    value = int(raw)
    if value < 0:
        raise ValueError("cache max size must be nonnegative")
    return value


def cache_directory():
    override = os.environ.get("RESEARCHCOMB_CACHE_DIR")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "researchcomb"
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        return Path(local) / "researchcomb" if local else Path.home() / "AppData" / "Local" / "researchcomb"
    return Path.home() / ".cache" / "researchcomb"


def normalize_url(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").rstrip(".").lower()
    default_port = (parsed.scheme == "https" and parsed.port == 443) or (parsed.scheme == "http" and parsed.port == 80)
    netloc = host if not parsed.port or default_port else f"{host}:{parsed.port}"
    return urlunsplit(((parsed.scheme or "https").lower(), netloc, parsed.path or "/", parsed.query, ""))


def cache_paths(url):
    normalized = normalize_url(url)
    digest = hashlib.sha256(f"{normalized}\n{USER_AGENT}".encode("utf-8")).hexdigest()
    directory = cache_directory()
    return directory, directory / f"{digest}.json", directory / f"{digest}.bin", normalized


def cache_control_no_store(value):
    if not value:
        return False
    return any(part.strip().lower().split("=", 1)[0].strip() == "no-store" for part in value.split(","))


def should_store_response(status, cache_control):
    if status == 429 or not (200 <= status < 207 and status not in {204, 205}):
        return False
    return not cache_control_no_store(cache_control)


def evict_cache(directory, budget):
    entries = []
    total = 0
    for meta_path in directory.glob("*.json"):
        body_path = meta_path.with_suffix(".bin")
        try:
            stored_at = json.loads(meta_path.read_text(encoding="utf-8")).get("stored_at", 0)
            size = body_path.stat().st_size if body_path.is_file() else 0
        except (OSError, TypeError, ValueError, json.JSONDecodeError, UnicodeError):
            continue
        entries.append((stored_at, meta_path, body_path, size))
        total += size
    entries.sort()
    for _, meta_path, body_path, size in entries:
        if total <= budget:
            break
        meta_path.unlink(missing_ok=True)
        body_path.unlink(missing_ok=True)
        total -= size


def load_cache(url):
    _, meta_path, body_path, normalized = cache_paths(url)
    if not meta_path.is_file() or not body_path.is_file():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        stored_at, ttl = meta.get("stored_at"), meta.get("ttl", DEFAULT_CACHE_TTL)
        if meta.get("url") != normalized or not isinstance(stored_at, (int, float)) or not isinstance(ttl, (int, float)):
            return None
        if time.time() - stored_at > ttl:
            return None
        return body_path.read_bytes()
    except (OSError, TypeError, ValueError, json.JSONDecodeError, UnicodeError):
        return None


def store_cache(url, body, status, cache_control):
    if not should_store_response(status, cache_control):
        return
    max_bytes = cache_max_bytes()
    if len(body) > max_bytes:
        return
    directory, meta_path, body_path, normalized = cache_paths(url)
    directory.mkdir(parents=True, exist_ok=True)
    meta_path.unlink(missing_ok=True)
    body_path.unlink(missing_ok=True)
    evict_cache(directory, max_bytes - len(body))
    meta = {"url": normalized, "stored_at": time.time(), "ttl": cache_ttl(), "status": status, "size": len(body), "user_agent": USER_AGENT}
    body_tmp, meta_tmp = body_path.with_name(body_path.name + ".tmp"), meta_path.with_name(meta_path.name + ".tmp")
    try:
        body_tmp.write_bytes(body)
        meta_tmp.write_text(json.dumps(meta), encoding="utf-8")
        body_tmp.replace(body_path)
        meta_tmp.replace(meta_path)
    except OSError:
        body_tmp.unlink(missing_ok=True)
        meta_tmp.unlink(missing_ok=True)


def write_output(body, output, overwrite):
    output = Path(output)
    temp_path = None
    created = False
    try:
        if overwrite:
            fd, temp_path = tempfile.mkstemp(dir=output.parent, prefix=".safe_fetch_")
            destination = os.fdopen(fd, "wb")
            created = True
        else:
            destination = output.open("xb")
            created = True
        destination.write(body)
        destination.close()
        if temp_path:
            Path(temp_path).replace(output)
            temp_path = None
    except BaseException:
        if created:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()
            elif not overwrite and output.exists():
                output.unlink(missing_ok=True)
        raise


def is_stub_or_challenge(body):
    if len(body) > 10240:
        return False
    text = body.lower()
    if b"http-equiv" in text and b"refresh" in text and b"content" in text:
        match = re.search(rb'content\s*=\s*["\']?(\d+)[^"\'<>]*["\']?\s+http-equiv\s*=\s*["\']?\s*refresh', text, re.I)
        if not match:
            match = re.search(rb'http-equiv\s*=\s*["\']?\s*refresh["\']?\s+content\s*=\s*["\']?(\d+)', text, re.I)
        if match and int(match.group(1)) < 5:
            return True
    if b"enable cookies" in text and b"pubmed.ncbi.nlm.nih.gov" in text:
        return True
    return False


def fetch(url, output, allow_private=False, overwrite=False, use_cache=None, no_cache=False):
    if allow_private:
        proxy_url = os.environ.get("HTTPS_PROXY", os.environ.get("HTTP_PROXY")) or \
                    os.environ.get("https_proxy", os.environ.get("http_proxy"))
        no_proxy = os.environ.get("NO_PROXY", os.environ.get("no_proxy", ""))
    else:
        proxy_url = None
        no_proxy = ""
    enabled_cache = cache_enabled(use_cache, no_cache, allow_private)
    
    for _ in range(MAX_REDIRECTS + 1):
        parsed, ip, port = public_endpoint(url, allow_private)
        if enabled_cache:
            cached = load_cache(url)
            if cached is not None:
                write_output(cached, output, overwrite)
                return url, len(cached)
        use_proxy = proxy_url and not in_no_proxy(parsed.hostname, no_proxy)
        
        if use_proxy:
            # Proxy does its own DNS resolution; local IP checks are advisory
            proxy_parsed = urlsplit(proxy_url if "://" in proxy_url else f"http://{proxy_url}")
            if proxy_parsed.scheme == "https":
                raise ValueError("https:// proxy URLs are not supported; use http:// for CONNECT proxies")
            if proxy_parsed.scheme != "http":
                raise ValueError("proxy URL must be HTTP")
            proxy_port = proxy_parsed.port or 8080
            
            if parsed.scheme == "https":
                options = {"timeout": 10, "context": ssl.create_default_context()}
                connection = http.client.HTTPSConnection(proxy_parsed.hostname, proxy_port, **options)
                connection.set_tunnel(parsed.hostname, port)
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
            # Pin to validated IP to prevent DNS rebinding (TLS SNI and hostname verification still use parsed.hostname)
            connection._create_connection = lambda address, timeout, source_address=None: socket.create_connection(
                (ip, port), timeout, source_address
            )
            target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        
        try:
            connection.request("GET", target, headers={"Connection": "close", "User-Agent": USER_AGENT})
            response = connection.getresponse()
            status = response.status
            cache_control = response.getheader("Cache-Control")
            if status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("redirect has no destination")
                url = urljoin(url, location)
                continue
            if not (200 <= status < 207 and status not in {204, 205}):
                raise ValueError(f"HTTP {status}")
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
                if enabled_cache:
                    store_cache(url, body, status, cache_control)
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
        use_cache = None
        no_cache = False
        url_arg = None
        output_arg = None
        
        for arg in args:
            if arg == "--allow-private":
                allow_private = True
            elif arg == "--overwrite":
                overwrite = True
            elif arg == "--cache":
                use_cache = True
            elif arg == "--no-cache":
                no_cache = True
            elif arg.startswith("--"):
                raise ValueError(f"unknown option: {arg}")
            elif url_arg is None:
                url_arg = arg
            elif output_arg is None:
                output_arg = arg
            else:
                raise ValueError("too many arguments")
        
        if url_arg is None or output_arg is None:
            raise ValueError("usage: safe_fetch.py [--allow-private] [--overwrite] [--cache] [--no-cache] URL OUTPUT_FILE")
        
        final_url, size = fetch(url_arg, output_arg, allow_private, overwrite, use_cache, no_cache)
        mode = " (private addresses allowed)" if allow_private else ""
        print(f"Saved {size} bytes from {final_url} to {output_arg}{mode}")
    except (OSError, ValueError, http.client.HTTPException) as error:
        sys.exit(f"FAIL: {error}")
