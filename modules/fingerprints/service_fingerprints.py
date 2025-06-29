import requests
from bs4 import BeautifulSoup


def detect_web_technology(url):
    """Detects web technologies using headers and HTML"""
    technologies = []

    try:
        response = requests.get(url, timeout=10, verify=False)
        headers = response.headers
        content = response.text

        # Detection by headers
        if "Server" in headers:
            technologies.append(f"Server: {headers['Server']}")

        if "X-Powered-By" in headers:
            technologies.append(f"Powered-By: {headers['X-Powered-By']}")

        # HTML Detection
        soup = BeautifulSoup(content, "html.parser")
        generator_meta = soup.find("meta", attrs={"name": "generator"})
        if generator_meta and "content" in generator_meta.attrs:
            technologies.append(f"Generator: {generator_meta['content']}")

        if '<script src="/wp-includes/' in content:
            technologies.append("CMS: WordPress")

    except Exception as e:
        technologies.append(f"Error: {str(e)}")

    return technologies


def detect_services(host, port_info):
    """Detecta servicios usando heurísticas simples basadas en nmap"""
    name = port_info.get("service", "").lower()
    version = port_info.get("version", "").lower()

    if "http" in name:
        if "apache" in version:
            return "Apache HTTP Server"
        elif "nginx" in version:
            return "Nginx"
        elif "iis" in version:
            return "Microsoft IIS"
        else:
            return "Generic HTTP Server"

    elif "ssh" in name:
        return "SSH Service"

    elif "mysql" in name or "mariadb" in version:
        return "MySQL/MariaDB"

    elif "ftp" in name:
        return "FTP Service"

    return f"Unknown Service: {name} {version}"
