# Fixing NVIDIA Model 404 Error

## Problem

Getting 404 "Function ... not found for account ..." means the model ID in `config.py` isn't available for your API key.

## Solution

### Option 1: Check Available Models (Recommended)

Run the model checker script:

```bash
source venv/bin/activate
python check_nvidia_models.py
```

This will test common model IDs and show which ones work with your API key.

### Option 2: Check NVIDIA AI Inference Dashboard

1. Go to https://build.nvidia.com/
2. Log in with your NVIDIA account
3. Navigate to "Functions" or "Models"
4. See which models are available/enabled for your account
5. Note the exact model ID format

### Option 3: Update Config with Common Models

The config has been updated with a fallback model. Common options:

**Llama Models (Most Common):**
- `meta/llama-3.1-8b-instruct` - Fast, smaller
- `meta/llama-3.1-70b-instruct` - Good balance (default)
- `meta/llama-3.1-405b-instruct` - Largest, most capable

**Mistral Models:**
- `mistralai/mistral-large`
- `mistralai/mixtral-8x22b-instruct`

**NVIDIA Models (if enabled):**
- `nvidia/nemotron-4-340b-instruct` - Original (requires enablement)
- `nvidia/llama-3.1-nemotron-70b-instruct`
- `nvidia/nemotron-70b-instruct`

## Steps to Fix

1. **Check available models:**
   ```bash
   source venv/bin/activate
   python check_nvidia_models.py
   ```

2. **Update config.py with an available model:**
   ```python
   NEMOTRON_MODEL = "meta/llama-3.1-70b-instruct"  # Or whatever works
   ```

3. **Restart the application:**
   ```bash
   python main.py demo/vulnerable_app yourusername/repo
   ```

## Quick Fix

If you want to use Llama 3.1 70B (most common):

```bash
# Edit config.py
nano config.py

# Change line 19 to:
NEMOTRON_MODEL = "meta/llama-3.1-70b-instruct"

# Save and run
python main.py demo/vulnerable_app yourusername/repo
```

## Verify Model Works

Test with a simple call:

```python
from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NEMOTRON_MODEL

client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
response = client.chat.completions.create(
    model=NEMOTRON_MODEL,
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=10
)
print(response.choices[0].message.content)
```

If this works, the model is available!

## Enable Nemotron-4 340B (if needed)

If you specifically need Nemotron-4 340B:

1. Go to https://build.nvidia.com/
2. Log in
3. Navigate to Functions/Models
4. Look for "Nemotron-4-340B-Instruct"
5. Enable it for your account (if available)
6. Wait for activation
7. Update config.py back to:
   ```python
   NEMOTRON_MODEL = "nvidia/nemotron-4-340b-instruct"
   ```

## Troubleshooting

### Still getting 404?
- Verify API key is correct in `.env`
- Check NVIDIA dashboard for account status
- Try a different model from the common list
- Check NVIDIA API documentation for latest model IDs

### Authentication errors?
- Verify `NVIDIA_API_KEY` in `.env`
- Check key hasn't expired
- Ensure key has proper permissions

### Model works but slow?
- Try a smaller model: `meta/llama-3.1-8b-instruct`
- Check your API quota/limits
- Reduce `max_tokens` in base_agent.py

