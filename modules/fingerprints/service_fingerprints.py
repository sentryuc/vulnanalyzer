#!/usr/bin/env python3

"""
Service Fingerprinting Module

Contains functions for detecting web technologies and services.
"""

import requests
import re
from urllib.parse import urljoin
import socket


def detect_web_technology(url, timeout=10):
    """
    Detect web technologies used by a website.
    
    Args:
        url (str): The URL to analyze
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Dictionary containing detected technologies
    """
    technologies = {
        'server': 'Unknown',
        'cms': 'Unknown',
        'framework': 'Unknown',
        'programming_language': 'Unknown',
        'javascript_frameworks': [],
        'cookies': [],
        'headers': {}
    }
    
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Make request
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        
        # Analyze headers
        headers = response.headers
        technologies['headers'] = dict(headers)
        
        # Server detection
        if 'Server' in headers:
            technologies['server'] = headers['Server']
        
        # X-Powered-By detection
        if 'X-Powered-By' in headers:
            powered_by = headers['X-Powered-By']
            if 'PHP' in powered_by:
                technologies['programming_language'] = 'PHP'
            elif 'ASP.NET' in powered_by:
                technologies['programming_language'] = 'ASP.NET'
        
        # Content analysis
        content = response.text.lower()
        
        # CMS Detection
        if 'wp-content' in content or 'wordpress' in content:
            technologies['cms'] = 'WordPress'
        elif 'joomla' in content:
            technologies['cms'] = 'Joomla'
        elif 'drupal' in content:
            technologies['cms'] = 'Drupal'
        
        # Framework Detection
        if 'django' in content:
            technologies['framework'] = 'Django'
            technologies['programming_language'] = 'Python'
        elif 'laravel' in content:
            technologies['framework'] = 'Laravel'
            technologies['programming_language'] = 'PHP'
        elif 'rails' in content or 'ruby' in content:
            technologies['framework'] = 'Ruby on Rails'
            technologies['programming_language'] = 'Ruby'
        
        # JavaScript Framework Detection
        js_frameworks = []
        if 'react' in content:
            js_frameworks.append('React')
        if 'angular' in content:
            js_frameworks.append('Angular')
        if 'vue' in content:
            js_frameworks.append('Vue.js')
        if 'jquery' in content:
            js_frameworks.append('jQuery')
        
        technologies['javascript_frameworks'] = js_frameworks
        
        # Cookie analysis
        if 'Set-Cookie' in headers:
            technologies['cookies'] = headers['Set-Cookie'].split(';')
        
    except requests.RequestException as e:
        technologies['error'] = str(e)
    except Exception as e:
        technologies['error'] = f"Unexpected error: {str(e)}"
    
    return technologies


def detect_services(host, ports=None, timeout=5):
    """
    Detect services running on specific ports.
    
    Args:
        host (str): Target host
        ports (list): List of ports to check, defaults to common ports
        timeout (int): Connection timeout in seconds
        
    Returns:
        dict: Dictionary of port -> service information
    """
    if ports is None:
        # Common ports to check
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 1433, 3306, 3389, 5432, 8080, 8443]
    
    services = {}
    
    for port in ports:
        try:
            service_info = _detect_service_on_port(host, port, timeout)
            if service_info:
                services[port] = service_info
        except Exception as e:
            # Continue checking other ports even if one fails
            continue
    
    return services


def _detect_service_on_port(host, port, timeout=5):
    """
    Detect service running on a specific port.
    
    Args:
        host (str): Target host
        port (int): Target port
        timeout (int): Connection timeout
        
    Returns:
        dict: Service information or None if no service detected
    """
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        
        if result != 0:
            sock.close()
            return None
        
        # Service detection based on port and banner grabbing
        service_info = {
            'port': port,
            'state': 'open',
            'name': _get_service_name(port),
            'banner': None,
            'version': 'Unknown'
        }
        
        # Try to grab banner
        try:
            # Send a simple request and read response
            if port in [80, 8080]:
                # HTTP service
                sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                service_info['banner'] = banner[:200]  # First 200 chars
                service_info['name'] = 'http'
                
                # Extract server info
                if 'Server:' in banner:
                    server_line = [line for line in banner.split('\n') if 'Server:' in line]
                    if server_line:
                        service_info['version'] = server_line[0].split('Server:')[1].strip()
                        
            elif port in [443, 8443]:
                # HTTPS service
                service_info['name'] = 'https'
                service_info['banner'] = 'SSL/TLS service'
                
            elif port == 22:
                # SSH service
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                service_info['banner'] = banner.strip()
                service_info['name'] = 'ssh'
                if 'SSH' in banner:
                    service_info['version'] = banner.strip()
                    
            elif port == 21:
                # FTP service
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                service_info['banner'] = banner.strip()
                service_info['name'] = 'ftp'
                
            elif port in [139, 445]:
                # SMB service
                service_info['name'] = 'smb'
                service_info['banner'] = 'SMB service detected'
                
            else:
                # Generic banner grab
                try:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    if banner:
                        service_info['banner'] = banner.strip()[:200]
                except:
                    pass
                    
        except Exception as e:
            # Banner grabbing failed, but port is open
            pass
        
        sock.close()
        return service_info
        
    except Exception as e:
        return None


def _get_service_name(port):
    """
    Get common service name for a port number.
    
    Args:
        port (int): Port number
        
    Returns:
        str: Service name
    """
    common_ports = {
        21: 'ftp',
        22: 'ssh',
        23: 'telnet',
        25: 'smtp',
        53: 'dns',
        80: 'http',
        110: 'pop3',
        143: 'imap',
        443: 'https',
        993: 'imaps',
        995: 'pop3s',
        1433: 'mssql',
        3306: 'mysql',
        3389: 'rdp',
        5432: 'postgresql',
        8080: 'http-alt',
        8443: 'https-alt'
    }
    
    return common_ports.get(port, f'unknown-{port}')


def analyze_ssl_certificate(host, port=443, timeout=10):
    """
    Analyze SSL certificate information.
    
    Args:
        host (str): Target host
        port (int): Target port (default 443)
        timeout (int): Connection timeout
        
    Returns:
        dict: SSL certificate information
    """
    import ssl
    
    cert_info = {
        'host': host,
        'port': port,
        'valid': False,
        'subject': None,
        'issuer': None,
        'version': None,
        'serial_number': None,
        'not_before': None,
        'not_after': None,
        'expired': None,
        'self_signed': False
    }
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                if cert:
                    cert_info['valid'] = True
                    cert_info['subject'] = dict(x[0] for x in cert.get('subject', []))
                    cert_info['issuer'] = dict(x[0] for x in cert.get('issuer', []))
                    cert_info['version'] = cert.get('version')
                    cert_info['serial_number'] = cert.get('serialNumber')
                    cert_info['not_before'] = cert.get('notBefore')
                    cert_info['not_after'] = cert.get('notAfter')
                    
                    # Check if certificate is expired
                    import datetime
                    try:
                        not_after = datetime.datetime.strptime(cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z')
                        cert_info['expired'] = not_after < datetime.datetime.now()
                    except:
                        cert_info['expired'] = None
                    
                    # Check if self-signed
                    subject_cn = cert_info['subject'].get('commonName', '')
                    issuer_cn = cert_info['issuer'].get('commonName', '')
                    cert_info['self_signed'] = subject_cn == issuer_cn
                    
    except Exception as e:
        cert_info['error'] = str(e)
    
    return cert_info
