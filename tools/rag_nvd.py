"""
RAG (Retrieval-Augmented Generation) system for NVD (National Vulnerability Database)
Provides rich, grounded context for CVE analysis by querying official NVD data
"""
import json
import os
import requests
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger("RAG_NVD")

# Try to import chromadb (optional dependency)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("⚠️  chromadb not installed. RAG features will be limited. Install with: pip install chromadb")

# ChromaDB setup
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COLLECTION_NAME = "nvd_cves"

# Local JSON files to load (if available)
LOCAL_FILES = ["cve-2024.json", "cve-2023.json"]


def load_local_cves(data_dir: str = None) -> int:
    """
    Load CVEs from local JSON files into ChromaDB
    
    Args:
        data_dir: Directory containing CVE JSON files (default: data/)
    
    Returns:
        Number of CVEs indexed
    """
    if not CHROMADB_AVAILABLE:
        logger.error("❌ chromadb is not installed. Install with: pip install chromadb")
        return 0
    
    if data_dir is None:
        data_dir = DATA_DIR
    
    if not os.path.exists(data_dir):
        logger.warning(f"⚠️  Data directory not found: {data_dir}")
        return 0
    
    logger.info(f"📚 Loading CVEs from local JSON files in {data_dir}...")
    
    # Initialize ChromaDB
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
    
    # Get or create collection
    try:
        collection = client.get_collection(COLLECTION_NAME)
        count = collection.count()
        if count > 0:
            logger.info(f"✅ Found existing collection with {count} CVEs")
            return count
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "NVD CVE database for RAG"}
        )
        logger.info("✅ Created new collection")
    
    total = 0
    
    # Load from local JSON files
    for filename in LOCAL_FILES:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"⚠️  Missing file: {path}")
            continue
        
        try:
            with open(path, "r", encoding='utf-8') as f:
                data = json.load(f)
                vulnerabilities = data.get("vulnerabilities", [])
                
                logger.info(f"📥 Loading {len(vulnerabilities)} CVEs from {filename}...")
                
                # Process CVEs in batches
                batch_size = 100
                batch_ids = []
                batch_docs = []
                batch_metas = []
                
                for item in vulnerabilities:
                    cve = item.get("cve", {})
                    cve_id = cve.get("id", "")
                    if not cve_id:
                        continue
                    
                    # Get description
                    descriptions = cve.get("descriptions", [])
                    description = ""
                    for desc in descriptions:
                        if desc.get("lang") == "en":
                            description = desc.get("value", "")
                            break
                    if not description:
                        continue
                    
                    # Get metrics
                    metrics = cve.get("metrics", {})
                    cvss_v3 = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
                    cvss_v2 = metrics.get("cvssMetricV2", [{}])[0] if metrics.get("cvssMetricV2") else {}
                    base_score = cvss_v3.get("cvssData", {}).get("baseScore") or cvss_v2.get("cvssData", {}).get("baseScore") or 0.0
                    
                    # Get published date
                    published = cve.get("published", "")
                    
                    # Create document text
                    doc_text = f"""CVE ID: {cve_id}
Published: {published}
CVSS Score: {base_score}/10
Description: {description}
"""
                    
                    batch_ids.append(cve_id)
                    batch_docs.append(doc_text.strip())
                    batch_metas.append({
                        "cve_id": cve_id,
                        "published": published,
                        "cvss_score": float(base_score),
                        "description": description[:500]
                    })
                    
                    # Add batch when full
                    if len(batch_ids) >= batch_size:
                        try:
                            collection.add(
                                ids=batch_ids,
                                documents=batch_docs,
                                metadatas=batch_metas
                            )
                            total += len(batch_ids)
                            logger.info(f"   ✅ Indexed {total} CVEs...")
                        except Exception as e:
                            logger.warning(f"   ⚠️  Error adding batch: {e}")
                        
                        batch_ids = []
                        batch_docs = []
                        batch_metas = []
                
                # Add remaining CVEs
                if batch_ids:
                    try:
                        collection.add(
                            ids=batch_ids,
                            documents=batch_docs,
                            metadatas=batch_metas
                        )
                        total += len(batch_ids)
                    except Exception as e:
                        logger.warning(f"   ⚠️  Error adding final batch: {e}")
                
                logger.info(f"✅ Loaded {len(vulnerabilities)} CVEs from {filename}")
                
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            continue
    
    logger.info(f"✅ Indexed {total} CVEs total into ChromaDB")
    logger.info(f"📁 Database location: {CHROMA_DIR}")
    
    return total


def download_nvd_data(year: int = 2024, max_cves: Optional[int] = None) -> list:
    """
    Download CVE data from NVD API (fallback if local files not available)
    
    Args:
        year: Year to download (default: 2024)
        max_cves: Maximum number of CVEs to download (None for all)
    
    Returns:
        List of CVE dictionaries
    """
    import time
    logger.info(f"📥 Downloading NVD data for year {year}...")
    
    # NVD API endpoint (free tier, no API key required)
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    params = {
        "pubStartDate": f"{year}-01-01T00:00:00.000",
        "pubEndDate": f"{year}-12-31T23:59:59.999",
        "resultsPerPage": 2000,  # Max per page
    }
    
    all_cves = []
    start_index = 0
    
    try:
        while True:
            params["startIndex"] = start_index
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])
            
            if not vulnerabilities:
                break
            
            for vuln in vulnerabilities:
                cve_data = vuln.get("cve", {})
                all_cves.append(cve_data)
                
                if max_cves and len(all_cves) >= max_cves:
                    logger.info(f"✅ Downloaded {len(all_cves)} CVEs (limited to {max_cves})")
                    return all_cves
            
            start_index += len(vulnerabilities)
            total_results = data.get("totalResults", 0)
            
            logger.info(f"📥 Downloaded {len(all_cves)}/{total_results} CVEs...")
            
            if start_index >= total_results:
                break
            
            # Rate limiting: NVD allows 5 requests per 30 seconds
            time.sleep(6)
        
        logger.info(f"✅ Downloaded {len(all_cves)} CVEs for year {year}")
        return all_cves
        
    except Exception as e:
        logger.error(f"❌ Error downloading NVD data: {e}")
        return all_cves


def build_vector_db(years: list = [2023, 2024], max_cves_per_year: Optional[int] = 1000, use_local: bool = True):
    """
    Build ChromaDB vector database from NVD data
    
    Args:
        years: List of years to download (default: [2023, 2024])
        max_cves_per_year: Maximum CVEs per year (None for all)
        use_local: Try to load from local JSON files first (default: True)
    """
    if not CHROMADB_AVAILABLE:
        logger.error("❌ chromadb is not installed. Install with: pip install chromadb")
        return
    
    logger.info("🔨 Building NVD vector database...")
    
    # Try loading from local files first
    if use_local:
        count = load_local_cves()
        if count > 0:
            logger.info(f"✅ Database built from local files with {count} CVEs")
            return
    
    # Fallback to API download
    logger.info("📥 No local files found, downloading from NVD API...")
    
    # Initialize ChromaDB
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
    
    # Get or create collection
    try:
        collection = client.get_collection(COLLECTION_NAME)
        logger.info(f"✅ Found existing collection with {collection.count()} CVEs")
        return
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "NVD CVE database for RAG"}
        )
        logger.info("✅ Created new collection")
    
    # Download and process CVEs
    all_cves = []
    for year in years:
        year_cves = download_nvd_data(year, max_cves_per_year)
        all_cves.extend(year_cves)
    
    if not all_cves:
        logger.warning("⚠️  No CVEs downloaded. Using empty database.")
        return
    
    # Process and add to ChromaDB
    logger.info(f"📚 Processing {len(all_cves)} CVEs into vector database...")
    
    ids = []
    documents = []
    metadatas = []
    
    for cve in all_cves:
        cve_id = cve.get("id", "")
        if not cve_id:
            continue
        
        # Extract key information
        descriptions = cve.get("descriptions", [])
        description = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break
        
        # Get metrics (CVSS scores)
        metrics = cve.get("metrics", {})
        cvss_v3 = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
        cvss_v2 = metrics.get("cvssMetricV2", [{}])[0] if metrics.get("cvssMetricV2") else {}
        
        base_score = cvss_v3.get("cvssData", {}).get("baseScore") or cvss_v2.get("cvssData", {}).get("baseScore") or 0.0
        
        # Get references
        references = cve.get("references", [])
        ref_urls = [ref.get("url", "") for ref in references[:5]]  # First 5 references
        
        # Get published date
        published = cve.get("published", "")
        
        # Create document text for embedding
        doc_text = f"""
CVE ID: {cve_id}
Published: {published}
CVSS Score: {base_score}
Description: {description}
References: {', '.join(ref_urls)}
"""
        
        ids.append(cve_id)
        documents.append(doc_text.strip())
        metadatas.append({
            "cve_id": cve_id,
            "published": published,
            "cvss_score": float(base_score),
            "description": description[:500]  # Truncate for metadata
        })
    
    # Add to ChromaDB in batches
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta
        )
        
        if (i + batch_size) % 500 == 0:
            logger.info(f"📚 Processed {min(i + batch_size, len(ids))}/{len(ids)} CVEs...")
    
    logger.info(f"✅ Vector database built with {collection.count()} CVEs")
    logger.info(f"📁 Database location: {CHROMA_DIR}")


def rag_nvd(cve_id: str, top_k: int = 3) -> str:
    """
    Retrieve relevant NVD context for a CVE using RAG
    
    Args:
        cve_id: CVE ID (e.g., "CVE-2023-30861")
        top_k: Number of similar CVEs to retrieve (default: 3)
    
    Returns:
        Formatted string with NVD context
    """
    if not CHROMADB_AVAILABLE:
        logger.warning("⚠️  chromadb not available. Returning basic CVE info.")
        return f"CVE ID: {cve_id}\nRAG database not available. Install chromadb and run setup_rag.py to enable full RAG features."
    
    try:
        # Initialize ChromaDB
        if not os.path.exists(CHROMA_DIR):
            logger.warning("⚠️  Vector database not found. Run 'python setup_rag.py' to build it.")
            return f"CVE ID: {cve_id}\nNVD vector database not found. Run 'python setup_rag.py' to build the database."
        
        client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False))
        
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except:
            logger.warning("⚠️  Collection not found. Building database...")
            # Try to load from local files
            load_local_cves()
            try:
                collection = client.get_collection(COLLECTION_NAME)
            except:
                logger.error("❌ Could not create collection. Database may be corrupted.")
                return f"CVE ID: {cve_id}\nError: Could not access vector database."
        
        # Query for exact CVE match first
        try:
            results = collection.get(ids=[cve_id])
            
            if results["ids"]:
                # Found exact match
                doc = results["documents"][0]
                metadata = results["metadatas"][0]
                
                logger.info(f"✅ Retrieved exact match for {cve_id}")
                
                # Format the context
                context = f"""
CVE ID: {cve_id}
Published: {metadata.get('published', 'Unknown')}
CVSS Score: {metadata.get('cvss_score', 0.0)}/10
Description: {metadata.get('description', doc)}
Full Details: {doc}
"""
                return context.strip()
        except:
            # CVE not found by exact match, try similarity search
            pass
        
        # If no exact match, try similarity search
        logger.info(f"🔍 No exact match for {cve_id}, searching similar CVEs...")
        
        # Create a query from the CVE ID
        query_text = f"CVE {cve_id}"
        
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        if results["ids"] and len(results["ids"][0]) > 0:
            # Use the most similar result
            doc = results["documents"][0][0]
            metadata = results["metadatas"][0][0]
            distance = results["distances"][0][0] if results.get("distances") else None
            
            logger.info(f"✅ Retrieved similar CVE (distance: {distance:.3f if distance else 'N/A'})")
            
            context = f"""
CVE ID: {metadata.get('cve_id', cve_id)}
Published: {metadata.get('published', 'Unknown')}
CVSS Score: {metadata.get('cvss_score', 0.0)}/10
Description: {metadata.get('description', doc)}
Full Details: {doc}
Note: This is a similar CVE retrieved via similarity search.
"""
            return context.strip()
        
        # Fallback: return basic info
        logger.warning(f"⚠️  No match found for {cve_id} in vector database")
        return f"CVE ID: {cve_id}\nNo detailed information available in the NVD vector database."
        
    except Exception as e:
        logger.error(f"❌ Error in RAG query: {e}")
        return f"CVE ID: {cve_id}\nError retrieving NVD context: {str(e)}"


if __name__ == "__main__":
    # Build the vector database (prefer local files)
    print("🔨 Building NVD vector database...")
    print("This will try to load from local JSON files first, then fall back to API...")
    print()
    
    # Try loading from local files first
    count = load_local_cves()
    
    if count == 0:
        # Fallback to API download
        print("📥 No local files found, downloading from NVD API...")
        build_vector_db(years=[2023, 2024], max_cves_per_year=1000, use_local=False)
    else:
        print(f"✅ Database ready with {count} CVEs from local files")
    
    # Test query
    print("\n🧪 Testing RAG query...")
    result = rag_nvd("CVE-2023-30861")
    print(result)
