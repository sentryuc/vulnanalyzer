#!/usr/bin/env python3

"""
VulnAnalyzer Core Module

This module contains the core functionality for the VulnAnalyzer framework:
- CalderaClient: Integration with MITRE Caldera
- VulnerabilityScanner: Network and vulnerability scanning
- Exploiter: Exploitation framework
- Utils: Utility functions
"""

__version__ = "1.0.0"
__author__ = "VulnAnalyzer Team"

# Import main classes for easier access
from .caldera_client import CalderaClient
from .scanner import VulnerabilityScanner  
from .exploiter import Exploiter
from . import utils

__all__ = [
    'CalderaClient',
    'VulnerabilityScanner', 
    'Exploiter',
    'utils'
]
