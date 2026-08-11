import ipaddress
import socket
import urllib.parse
from typing import Any, Dict, Optional
import httpx


def validate_url_ssrf_safety(url_str: str) -> str:
    """Validates URL protocol, resolves DNS, and checks against private/loopback/cloud metadata IP blocklists."""
    try:
        parsed = urllib.parse.urlparse(url_str)
    except Exception as exc:
        raise ValueError(f"Malformed HTTP URL: {exc}")

    scheme = (parsed.scheme or "").lower()
    if scheme not in ["http", "https"]:
        raise ValueError(f"Security Policy Violation: Only 'http' and 'https' protocols are permitted. Received '{scheme}'.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: Hostname is required.")

    if hostname.lower() in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
        raise ValueError("Security Policy Violation (SSRF): Connection to localhost or loopback address is prohibited.")

    # DNS Resolution & IP Audit
    try:
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if scheme == "https" else 80), socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"DNS Resolution Failed for host '{hostname}': {e}")

    for family, socktype, proto, canonname, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        # SSRF Blocklist Check
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
            or str(ip_obj) == "169.254.169.254"
        ):
            raise ValueError(f"Security Policy Violation (SSRF): Host '{hostname}' resolved to prohibited IP range '{ip_str}'.")

    return url_str


class HTTPRequestExecutor:
    """Executes external HTTP requests with strict SSRF blocklist checking and payload limits."""

    @staticmethod
    async def execute_request(
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 10.0,
        max_bytes: int = 2 * 1024 * 1024,  # 2 MB limit
    ) -> Dict[str, Any]:
        try:
            safe_url = validate_url_ssrf_safety(url)
            http_method = (method or "GET").upper()

            if http_method not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                raise ValueError(f"Unsupported HTTP method '{http_method}'. Supported methods: GET, POST, PUT, PATCH, DELETE.")

            req_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in ["authorization", "cookie", "x-api-key"]}

            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
                response = await client.request(
                    method=http_method,
                    url=safe_url,
                    headers=req_headers,
                    params=params,
                    json=json_body,
                )

                # Limit response body size
                content_bytes = response.content
                if len(content_bytes) > max_bytes:
                    raise ValueError(f"HTTP Response size ({len(content_bytes)} bytes) exceeded maximum allowed limit ({max_bytes} bytes).")

                # Try parsing JSON
                try:
                    res_payload = response.json()
                except Exception:
                    res_payload = response.text

                return {
                    "status_code": response.status_code,
                    "url": str(response.url),
                    "method": http_method,
                    "headers": dict(response.headers),
                    "body": res_payload,
                    "is_success": response.is_success,
                }

        except ValueError as val_err:
            return {
                "status_code": 400,
                "error": f"SSRF Blocked: {str(val_err)}",
                "is_success": False,
                "body": None,
            }
        except httpx.TimeoutException:
            raise TimeoutError(f"HTTP Request to '{url}' timed out after {timeout_seconds} seconds.")
        except httpx.RequestError as req_err:
            raise RuntimeError(f"HTTP Request failed: {req_err}")


http_executor = HTTPRequestExecutor()
