#!/usr/bin/env python3

import random
import string
import hashlib
import os
import json
import socket
import re
from datetime import datetime
import ipaddress


def generate_random_string(length=8):
    """Generate a random string of specified length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def generate_random_id():
    """Generate a random ID for operations."""
    return generate_random_string(16)


def hash_string(text):
    """Generate SHA256 hash of a string."""
    return hashlib.sha256(text.encode()).hexdigest()


def validate_ip(ip):
    """Validate if a string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_url(url):
    """Basic URL validation."""
    return url.startswith(('http://', 'https://'))


def get_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def format_bytes(bytes_size):
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def safe_filename(filename):
    """Make a filename safe for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def ensure_directory(directory):
    """Ensure directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def load_json_file(filepath):
    """Safely load a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": str(e)}


def save_json_file(data, filepath):
    """Safely save data to a JSON file."""
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        return {"error": str(e)}


def parse_port_range(port_range):
    """Parse port range string to list of ports."""
    ports = []
    try:
        if ',' in port_range:
            # Multiple ports/ranges separated by comma
            parts = port_range.split(',')
            for part in parts:
                ports.extend(parse_single_port_range(part.strip()))
        else:
            ports.extend(parse_single_port_range(port_range))
    except ValueError:
        pass
    return sorted(list(set(ports)))


def parse_single_port_range(port_str):
    """Parse a single port or port range."""
    if '-' in port_str:
        # Port range
        start, end = map(int, port_str.split('-'))
        return list(range(start, end + 1))
    else:
        # Single port
        return [int(port_str)]


def is_port_open(host, port, timeout=3):
    """Check if a port is open on a host."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_local_ip():
    """Get local IP address."""
    import socket
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def format_scan_duration(start_time, end_time):
    """Format scan duration for display."""
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"


def parse_target(target):
    """Parse target string to extract host and determine target type."""
    target = target.strip()
    
    # Remove protocol if present
    if target.startswith(('http://', 'https://')):
        target = target.split('://', 1)[1]
    
    # Remove path if present
    if '/' in target:
        target = target.split('/')[0]
    
    # Handle port specification
    host = target
    port = None
    
    if ':' in target and not target.startswith('['):  # IPv4 with port
        parts = target.split(':')
        if len(parts) == 2 and parts[1].isdigit():
            host = parts[0]
            port = int(parts[1])
    elif target.startswith('[') and ']:' in target:  # IPv6 with port
        match = re.match(r'\[([^\]]+)\]:(\d+)', target)
        if match:
            host = match.group(1)
            port = int(match.group(2))
    
    return {
        'host': host,
        'port': port,
        'original': target,
        'type': _determine_target_type(host)
    }


def is_valid_target(target):
    """Validate if target is a valid IP address or domain name."""
    try:
        parsed = parse_target(target)
        host = parsed['host']
        
        # Try to validate as IP address
        try:
            ipaddress.ip_address(host)
            return True
        except ipaddress.AddressValueError:
            pass
        
        # Validate as domain name
        if _is_valid_domain(host):
            return True
        
        return False
    except Exception:
        return False


def _determine_target_type(host):
    """Determine if target is IPv4, IPv6, or domain."""
    try:
        ip = ipaddress.ip_address(host)
        if isinstance(ip, ipaddress.IPv4Address):
            return 'ipv4'
        elif isinstance(ip, ipaddress.IPv6Address):
            return 'ipv6'
    except ipaddress.AddressValueError:
        if _is_valid_domain(host):
            return 'domain'
    
    return 'unknown'


def _is_valid_domain(domain):
    """Check if string is a valid domain name."""
    if len(domain) > 255:
        return False
    
    # Remove trailing dot if present
    if domain.endswith('.'):
        domain = domain[:-1]
    
    # Check each label
    labels = domain.split('.')
    if len(labels) < 2:
        return False
    
    for label in labels:
        if not label or len(label) > 63:
            return False
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', label):
            return False
    
    return True
