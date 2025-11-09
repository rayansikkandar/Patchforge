#!/usr/bin/env python3
"""
Setup script to build the NVD vector database for RAG
Run this once before using PatchForge to enable RAG-powered CVE analysis
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.rag_nvd import build_vector_db, rag_nvd

def main():
    print("🔨 PatchForge RAG Setup")
    print("=" * 50)
    print()
    print("This script will:")
    print("  1. Download CVE data from NVD (National Vulnerability Database)")
    print("  2. Build a vector database for RAG-powered CVE analysis")
    print("  3. Enable grounded, authoritative CVE explanations")
    print()
    print("⚠️  This may take 10-30 minutes depending on your internet connection")
    print("    The database will be saved in ./chroma_nvd/")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    print()
    print("📥 Downloading NVD data for 2023 and 2024...")
    print("   (Limited to 1000 CVEs per year for faster setup)")
    print()
    
    try:
        # Build vector database
        build_vector_db(years=[2023, 2024], max_cves_per_year=1000)
        
        print()
        print("✅ Vector database built successfully!")
        print()
        print("🧪 Testing RAG query...")
        
        # Test query
        test_result = rag_nvd("CVE-2023-30861")
        print(test_result)
        
        print()
        print("✅ Setup complete! PatchForge is ready to use RAG-powered CVE analysis.")
        print()
        print("💡 Tip: For a more comprehensive database, run:")
        print("   python tools/rag_nvd.py")
        print("   (without year/count limits)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

