import random
import string
import re
import os
import ipaddress
from urllib.parse import urlparse


def parse_target(target):
    """Parsea y valida el objetivo (IP, rango, dominio)"""
    # Verificar si es una URL
    if target.startswith(("http://", "https://")):
        return target

    # Verificar si es un rango CIDR
    try:
        ipaddress.IPv4Network(target)
        return target
    except ValueError:
        pass

    # Verificar si es una IP individual
    try:
        ipaddress.IPv4Address(target)
        return target
    except ValueError:
        pass

    # Asumir que es un nombre de dominio
    return target


def is_valid_target(target):
    """Verifica si el objetivo es válido"""
    # Validar URL
    if target.startswith(("http://", "https://")):
        try:
            result = urlparse(target)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    # Validar IP o rango CIDR
    try:
        ipaddress.IPv4Network(target)
        return True
    except ValueError:
        try:
            ipaddress.IPv4Address(target)
            return True
        except ValueError:
            pass

    # Validar nombre de dominio
    domain_pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(domain_pattern, target))


def get_exploit_path():
    """Obtiene la ruta al directorio de exploits"""
    # Obtener la ruta base del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "modules", "exploits")


def get_user_agent():
    """Devuelve un User-Agent aleatorio"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    ]
    return random.choice(user_agents)


# Method from caldera
def generate_random_string(length=8):
    """Genera una cadena aleatoria de longitud especificada"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
