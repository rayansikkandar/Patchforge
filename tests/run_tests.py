#!/usr/bin/env python3
"""
Test runner for PatchForge
Runs unit tests and integration tests
"""
import sys
import subprocess
import os


def main():
    """Run all tests"""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    print("🧪 Running PatchForge Test Suite\n")
    print("=" * 60)
    
    # Run unit tests (exclude integration tests)
    print("\n📋 Running Unit Tests...")
    print("-" * 60)
    result_unit = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "-m", "not integration",
            "--tb=short"
        ],
        cwd=project_root
    )
    
    # Run integration tests (if requested or if unit tests pass)
    if result_unit.returncode == 0:
        print("\n🔗 Running Integration Tests...")
        print("-" * 60)
        print("Note: Integration tests require real API calls or proper mocks")
        print("      They may take longer and require network access\n")
        
        result_integration = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "-m", "integration",
                "--tb=short",
                "--timeout=300"  # 5 minute timeout for integration tests
            ],
            cwd=project_root
        )
        
        if result_integration.returncode != 0:
            print("\n⚠️  Integration tests had failures (this may be expected without API keys)")
    
    # Summary
    print("\n" + "=" * 60)
    if result_unit.returncode == 0:
        print("✅ Unit tests passed!")
    else:
        print("❌ Unit tests failed!")
        sys.exit(1)
    
    print("\n💡 Tip: Run with pytest directly for more options:")
    print("   pytest tests/ -v                    # All tests")
    print("   pytest tests/ -v -m integration      # Integration only")
    print("   pytest tests/test_validator.py -v    # Specific test file")


if __name__ == "__main__":
    main()

