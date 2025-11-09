import requests
from typing import List, Dict
from datetime import datetime
from config import NVD_API_URL, NVD_API_KEY, MIN_CVSS_SCORE, MIN_CVE_YEAR
from utils.logger import setup_logger

logger = setup_logger("NVD")

class NVDClient:
    def __init__(self):
        self.base_url = NVD_API_URL
        self.headers = {}
        if NVD_API_KEY:
            self.headers["apiKey"] = NVD_API_KEY
    
    def search_cve_by_keyword(self, keyword: str) -> List[Dict]:
        """Search CVEs by package name"""
        try:
            logger.info(f"Searching CVEs for: {keyword}")
            response = requests.get(
                self.base_url,
                params={"keywordSearch": keyword},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            cves = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_id = cve.get("id")
                
                # Extract CVSS score
                metrics = cve.get("metrics", {})
                cvss_score = 0
                if "cvssMetricV31" in metrics:
                    cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                elif "cvssMetricV2" in metrics:
                    cvss_score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]
                
                # Extract year from CVE ID (e.g., CVE-1999-0974 -> 1999)
                cve_year = None
                if cve_id:
                    parts = cve_id.split("-")
                    if len(parts) >= 2:
                        try:
                            cve_year = int(parts[1])
                        except (ValueError, IndexError):
                            pass
                
                # Filter by CVSS score and year
                if cvss_score >= MIN_CVSS_SCORE:
                    # Skip very old CVEs (they often have outdated/incompatible fixes)
                    if cve_year and cve_year < MIN_CVE_YEAR:
                        logger.debug(f"Skipping old CVE {cve_id} (year: {cve_year})")
                        continue
                    
                    cves.append({
                        "cve_id": cve_id,
                        "cvss_score": cvss_score,
                        "description": cve.get("descriptions", [{}])[0].get("value", ""),
                        "published": cve.get("published", ""),
                        "cve_year": cve_year
                    })
            
            logger.info(f"Found {len(cves)} high-severity CVEs")
            return cves
            
        except Exception as e:
            logger.error(f"NVD API error: {e}")
            return []
    
    def get_cve_details(self, cve_id: str) -> Dict:
        """Get detailed CVE information"""
        try:
            response = requests.get(
                self.base_url,
                params={"cveId": cve_id},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("vulnerabilities"):
                return data["vulnerabilities"][0]["cve"]
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching CVE {cve_id}: {e}")
            return {}

