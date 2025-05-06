import nmap
import requests
from concurrent.futures import ThreadPoolExecutor
from core.utils import parse_target, is_valid_target

from modules.fingerprints.service_fingerprints import (
    detect_web_technology,
    detect_services,
)


class VulnerabilityScanner:
    def __init__(self, target, scan_type="full", threads=10):
        self.target = parse_target(target)
        self.scan_type = scan_type
        self.threads = threads
        self.results = {}
        self.nm = nmap.PortScanner()

    def scan_network(self):
        print(f"[*] Starting network scan on {self.target}")

        # Define scan types
        scan_types = {
            "quick": "-F -T4",  # Quick scan
            "full": "-sS -sV -O -A -T4",  # Full scan with OS detection
            "stealth": "-sS -T2",  # Stealth scanning
        }

        args = scan_types.get(self.scan_type, scan_types["full"])

        try:
            self.nm.scan(hosts=self.target, arguments=args)
        except Exception as e:
            print(f"[!] Error running Nmap: {e}")
            return {}

        for host in self.nm.all_hosts():
            try:
                host_state = self.nm[host].state()
                os_matches = self.nm[host].get("osmatch", [])
                self.results[host] = {
                    "status": host_state,
                    "ports": {},
                    "os": os_matches,
                    "vulnerabilities": [],
                }

                for proto in self.nm[host].all_protocols():
                    for port in self.nm[host][proto]:
                        service = self.nm[host][proto][port]
                        fingerprint = detect_services(host, service)
                        product = service.get("product", "")
                        version = service.get("version", "")
                        full_version = f"{product} {version}".strip()

                        self.results[host]["ports"][port] = {
                            "state": service["state"],
                            "service": service["name"],
                            "version": full_version,
                            "fingerprint": fingerprint,
                        }
            except Exception as e:
                print(f"[!] Error processing host {host}: {e}")

        return self.results

    def scan_web_vulnerabilities(self, urls=None):
        """Scans web vulnerabilities on the provided URLs"""
        if not urls:
            # Extract URLs from scanned hosts with web ports (80, 443, 8080, etc.)
            urls = []
            web_ports = [80, 443, 8080, 8443, 8000, 8888]

            for host in self.results:
                for port in web_ports:
                    if port in self.results[host]["ports"]:
                        protocol = "https" if port in [443, 8443] else "http"
                        urls.append(f"{protocol}://{host}:{port}")

        print(f"[*] Scanning web vulnerabilities is {len(urls)} URLs")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            web_results = list(executor.map(self._scan_single_web_target, urls))

        # Procesar y agregar resultados
        for url, result in zip(urls, web_results):
            host = url.split("://")[1].split(":")[0]
            if host in self.results:
                self.results[host]["web_vulnerabilities"] = result

        return self.results

    def _scan_single_web_target(self, url):
        """Scans a single URL for web vulnerabilities"""
        result = {
            "url": url,
            "technologies": detect_web_technology(url),
            "vulnerabilities": [],
        }

        # Check security headers
        try:
            response = requests.get(url, timeout=10, verify=False)
            headers = response.headers

            security_headers = {
                "X-XSS-Protection": "Missing XSS protection header",
                "X-Content-Type-Options": "Missing content type options header",
                "X-Frame-Options": "Missing clickjacking protection",
                "Content-Security-Policy": "Missing content security policy",
                "Strict-Transport-Security": "Missing HSTS header",
            }

            for header, issue in security_headers.items():
                if header not in headers:
                    result["vulnerabilities"].append(
                        {
                            "type": "missing_security_header",
                            "name": issue,
                            "severity": "medium",
                        }
                    )

        except Exception as e:
            result["error"] = str(e)

        return result

    def run(self):
        """Run the full scan"""
        self.scan_network()
        self.scan_web_vulnerabilities()
        return self.results
