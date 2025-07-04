

import subprocess
import re
import json

class HostDiscoverer:
    """
    Discovers active hosts on a given network range using nmap.
    """

    def __init__(self, network_range):
        """
        Initializes the HostDiscoverer.

        :param network_range: The network range to scan (e.g., "192.168.1.0/24").
        """
        if not self._is_valid_network_range(network_range):
            raise ValueError(f"Invalid network range provided: {network_range}")
        self.network_range = network_range
        self.active_hosts = []

    def _is_valid_network_range(self, network_range):
        """
        Validates the network range format.
        """
        # A simple regex to validate CIDR notation, e.g., 192.168.1.0/24
        pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})$"
        return re.match(pattern, network_range)

    def discover_hosts(self):
        """
        Runs an nmap ping scan (-sn) to discover active hosts.
        """
        print(f"[*] Discovering hosts in {self.network_range} with nmap...")
        try:
            # -sn: Ping Scan - disables port scan
            # -T4: Aggressive timing template for faster execution
            command = ["nmap", "-sn", "-T4", self.network_range]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )

            # Parse the output to find IP addresses
            self.active_hosts = re.findall(
                r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", result.stdout
            )
            
            print(f"[+] Found {len(self.active_hosts)} active hosts.")
            return self.active_hosts

        except FileNotFoundError:
            print("\n[!] Error: 'nmap' is not installed or not in your PATH.")
            print("Please install nmap to use this feature.")
            return []
        except subprocess.CalledProcessError as e:
            print(f"\n[!] Error during nmap scan: {e}")
            print(f"Stderr: {e.stderr}")
            return []
        except Exception as e:
            print(f"\n[!] An unexpected error occurred: {e}")
            return []

    def get_results_as_json(self):
        """
        Returns the list of active hosts in JSON format.
        """
        return json.dumps({"active_hosts": self.active_hosts}, indent=4)

