import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
NVD_API_KEY = os.getenv("NVD_API_KEY")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
# Common model IDs (update based on what's available for your API key):
# - "meta/llama-3.1-70b-instruct" (common default)
# - "meta/llama-3.1-8b-instruct" (faster, smaller)
# - "meta/llama-3.1-405b-instruct" (largest)
# - "mistralai/mistral-large"
# - "nvidia/nemotron-4-340b-instruct" (if enabled in your account)
# - "nvidia/llama-3.1-nemotron-70b-instruct"
# Run: python check_nvidia_models.py to see what's available for your account
NEMOTRON_MODEL = "meta/llama-3.1-70b-instruct"  # Default fallback

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
GITHUB_API_URL = "https://api.github.com"

MIN_CVSS_SCORE = 7.0  # Only patch HIGH/CRITICAL CVEs
MIN_CVE_YEAR = 2015  # Only process CVEs from this year onwards (filters out ancient CVEs)
PREFER_RECENT_CVES = True  # Prefer CVEs from 2020+ for better compatibility

# ReAct Loop Configuration
MAX_RETRIES = 3  # Maximum number of retry attempts for patch refinement

