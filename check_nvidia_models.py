#!/usr/bin/env python3
"""
Check available NVIDIA models for your API key
"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

if not NVIDIA_API_KEY or NVIDIA_API_KEY == "your_nvidia_api_key_here":
    print("❌ NVIDIA_API_KEY not set in .env")
    sys.exit(1)

print("🔍 Checking available NVIDIA models for your API key...")
print("=" * 60)
print()

# Common NVIDIA model IDs to try
common_models = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.1-405b-instruct",
    "mistralai/mistral-large",
    "mistralai/mixtral-8x22b-instruct",
    "google/gemma-2-9b-it",
    "google/gemma-2-27b-it",
    "nvidia/nemotron-4-340b-instruct",
    "nvidia/nemotron-4-340b-reward",
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "nvidia/nemotron-70b-instruct",
]

print("Testing common model IDs...")
print()

client = OpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

available_models = []
unavailable_models = []

for model in common_models:
    try:
        # Try a simple completion to check if model is available
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        available_models.append(model)
        print(f"✅ {model} - AVAILABLE")
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            unavailable_models.append(model)
            print(f"❌ {model} - NOT AVAILABLE")
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            print(f"⚠️  {model} - AUTH ERROR (check API key)")
        else:
            # Might be available but had a different error
            print(f"⚠️  {model} - ERROR: {error_msg[:50]}")

print()
print("=" * 60)
print()

if available_models:
    print("✅ Available models for your account:")
    for model in available_models:
        print(f"   - {model}")
    print()
    print("💡 Update NEMOTRON_MODEL in config.py to use one of these:")
    print(f"   NEMOTRON_MODEL = \"{available_models[0]}\"")
else:
    print("⚠️  No models found from the common list.")
    print()
    print("Try checking your NVIDIA AI Inference dashboard:")
    print("   https://build.nvidia.com/")
    print()
    print("Or check the API documentation for available models:")
    print("   https://docs.nvidia.com/nim/")

print()
print("=" * 60)

