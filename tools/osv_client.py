import requests
from utils.logger import setup_logger

logger = setup_logger("OSV")

class OSVClient:
    """
    Client for OSV (Open Source Vulnerabilities) API
    Better than NVD for exact package+version matching
    https://osv.dev/
    """
    
    def __init__(self):
        self.base_url = "https://api.osv.dev/v1"
    
    def query_package(self, package_name: str, version: str, ecosystem: str) -> list:
        """
        Query OSV for vulnerabilities in a specific package+version
        
        Args:
            package_name: e.g., "flask"
            version: e.g., "2.0.1"
            ecosystem: e.g., "PyPI", "npm"
        
        Returns:
            List of vulnerabilities
        """
        try:
            logger.info(f"Querying OSV: {ecosystem}/{package_name}@{version}")
            
            response = requests.post(
                f"{self.base_url}/query",
                json={
                    "package": {
                        "name": package_name,
                        "ecosystem": ecosystem
                    },
                    "version": version
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            vulns = data.get('vulns', [])
            
            if vulns:
                logger.warning(f"Found {len(vulns)} vulnerabilities")
            else:
                logger.info("No vulnerabilities found")
            
            return vulns
            
        except Exception as e:
            logger.error(f"OSV API error: {e}")
            return []
    
    def get_vulnerability_details(self, vuln_id: str) -> dict:
        """Get detailed information about a vulnerability"""
        try:
            response = requests.get(
                f"{self.base_url}/vulns/{vuln_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching {vuln_id}: {e}")
            return {}

