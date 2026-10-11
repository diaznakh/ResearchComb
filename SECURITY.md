# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in ResearchComb, please report it via [GitHub's private vulnerability reporting](https://github.com/diaznakh/ResearchComb/security/advisories/new). This allows us to coordinate disclosure and prepare fixes before public announcement.

Alternatively, you may contact the maintainers directly through GitHub.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within 48 hours and will work with you to coordinate responsible disclosure.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.5.23  | ✅ Yes    |
| 0.5.22  | ❌ No     |
| < 0.5.22| ❌ No     |

Only the latest version receives security updates. Please upgrade to the most recent release.

## Security Scope

ResearchComb's security surface includes:

1. **`safe_fetch.py`:** SSRF protections (DNS rebinding, private address validation, redirect handling, TLS verification)
2. **`check_completion.py`:** Input validation for evidence records and manuscript checking
3. **Skill instructions:** Guidance on isolating third-party code execution, preventing prompt injection, and treating fetched content as untrusted data

Security issues in these areas are in scope. Issues in AI host implementations (browsers, execution sandboxes, prompt handling) are the host's responsibility.

## Known Limitations

- **Prompt injection:** ResearchComb processes untrusted web content (papers, abstracts, code repositories). AI hosts must treat fetched content as data, not instructions. See skill documentation for guidance.
- **Proxy mode:** When using `--allow-private` with proxies, the proxy performs DNS resolution; local IP checks are advisory.
- **Host dependencies:** Security relies on host AI capabilities (TLS verification, DNS resolution, execution isolation).
