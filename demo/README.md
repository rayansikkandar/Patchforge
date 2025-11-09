# PatchForge Demo

## Setup

1. Install dependencies:

```bash
pip install -r ../requirements.txt
```

2. Set environment variables:

```bash
cp ../.env.example ../.env
# Edit .env with your keys
```

3. Run PatchForge:

```bash
python ../main.py ./vulnerable_app yourusername/demo-repo
```

## What Happens

1. **Scanner** finds CVE-2023-30861 in Flask 2.0.1

2. **Researcher** analyzes the vulnerability

3. **PatchGenerator** upgrades Flask to 2.3.2

4. **Validator** tests the patch

5. **PRCreator** opens a GitHub PR

## Demo Tips

- Use a test repository you control

- Run with `--verbose` flag for detailed logs

- The PR will appear in real-time on GitHub

