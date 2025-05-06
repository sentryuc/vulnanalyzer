from dotenv import load_dotenv
import os

load_dotenv()

# General settings
DEBUG = True
VERSION = "1.0.0"

# MITRE Caldera Settings
CALDERA_BASE_URL = os.getenv("CALDERA_BASE_URL", "http://localhost:8888")
CALDERA_API_KEY = os.getenv("CALDERA_API_KEY", "")

# Scan Settings
DEFAULT_SCAN_TYPE = "full"
DEFAULT_THREADS = 10
DEFAULT_TIMEOUT = 30

# Report Configuration
REPORT_COMPANY_NAME = "VulnAnalyzer"
# REPORT_LOGO_PATH = "reports/templates/logo.png"

# Logging Setting
LOG_LEVEL = "INFO"
LOG_FILE = "vulnanalyzer.log"

# Exploit Settings
EXPLOIT_TIMEOUT = 60
