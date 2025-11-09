#!/usr/bin/env python3
"""
Setup script to build the NVD vector database for RAG
Run this once before using PatchForge to enable RAG-powered CVE analysis

This script will:
1. Try to load from local JSON files in data/ directory (fastest)
2. Fall back to downloading from NVD API if local files not found
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.rag_nvd import build_vector_db, load_local_cves, rag_nvd

def main():
    print("🔨 PatchForge RAG Setup")
    print("=" * 50)
    print()
    print("This script will:")
    print("  1. Try to load CVEs from local JSON files in data/ directory (fastest)")
    print("  2. Fall back to downloading from NVD API if local files not found")
    print("  3. Build a vector database for RAG-powered CVE analysis")
    print()
    
    # Check for local data directory
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if os.path.exists(data_dir):
        print(f"✅ Found data directory: {data_dir}")
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        if files:
            print(f"   Found {len(files)} JSON file(s): {', '.join(files)}")
            print("   Will load from local files (fast!)")
        else:
            print("   No JSON files found, will download from API")
    else:
        print(f"⚠️  Data directory not found: {data_dir}")
        print("   Will download from NVD API (slower)")
        print()
        print("💡 Tip: To use local files, create data/ directory and add CVE JSON files:")
        print("   - data/cve-2024.json")
        print("   - data/cve-2023.json")
        print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    print()
    
    # Try loading from local files first
    print("📚 Attempting to load from local JSON files...")
    count = load_local_cves()
    
    if count > 0:
        print()
        print(f"✅ Vector database built successfully from local files!")
        print(f"   Indexed {count} CVEs")
    else:
        print()
        print("📥 No local files found, downloading from NVD API...")
        print("   (This may take 10-30 minutes depending on your connection)")
        print()
        
        # Build from API
        build_vector_db(years=[2023, 2024], max_cves_per_year=1000, use_local=False)
    
    print()
    print("🧪 Testing RAG query...")
    
    # Test query
    test_result = rag_nvd("CVE-2023-30861")
    print(test_result)
    
    print()
    print("✅ Setup complete! PatchForge is ready to use RAG-powered CVE analysis.")
    print()
    print("💡 To add more CVEs, place JSON files in the data/ directory and run this script again.")

if __name__ == "__main__":
    main()
