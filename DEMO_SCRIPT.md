# PatchForge Demo Script

## Setup (Before Demo)

1. Ensure `patchforge-demo` repo exists on your GitHub
2. Test PatchForge on it at least 3 times
3. Have GitHub open in browser (not logged in to your account - use incognito)
4. Terminal ready with PatchForge directory
5. Backup: Screen recording of successful run

## The Demo (90 seconds)

### [0:00-0:15] The Problem

**Say:** "Every day, developers ship code with hidden time bombs—outdated dependencies with critical vulnerabilities. Manual patching is slow and error-prone. We built PatchForge to solve this autonomously."

**Do:** Start terminal, show PatchForge banner

### [0:15-0:30] Connect & Scan

**Say:** "PatchForge connects to GitHub and scans your dependencies against vulnerability databases."

**Do:** 
- Enter your GitHub username
- Select `patchforge-demo` repository
- Press Enter to start

### [0:30-1:00] Watch the Agents

**Say:** "Watch our five AI agents work together: Scanner finds seven critical CVEs. Researcher identifies secure versions. Patcher updates the requirements file. Validator confirms no conflicts. PR Creator pushes to GitHub—all autonomous."

**Do:**
- Watch the animated progress
- Point to key moments:
  - "There - CVE-2023-30861, CVSS 9.8"
  - "Upgrading Flask 2.0.1 to 2.3.3"
  - "Validation passed"

### [1:00-1:30] The Result

**Say:** "Seventy-three seconds from critical vulnerability to merge-ready pull request."

**Do:**
- Show PR URL in terminal
- Switch to browser
- Pull up the GitHub PR (already open in tab)
- Show PR description with CVE details, diff, validation results

### [1:30-1:45] The Wow

**Say:** "This isn't just code generation—it's autonomous security remediation. It found the vulnerability, researched the fix, tested it, and submitted a PR. No human intervention required."

**Do:**
- Scroll through PR showing:
  - Professional description
  - CVE links
  - Test results
  - Clean diff (one line changed)

### [1:45-2:00] The Impact

**Say:** "Every company has hundreds of dependencies. PatchForge can scan entire organizations and patch vulnerabilities at machine speed. That's the power of agentic AI."

**Do:**
- Return to terminal
- Show final summary stats

## Backup Plans

**If live demo fails:**
1. "Let me show you a recording from our testing" → Play backup video
2. Show existing PR on GitHub from previous run
3. Walk through code and architecture

**If GitHub is slow:**
- Keep talking through the agent steps
- "GitHub's API is processing... normally this takes 60-90 seconds"

**If questions during demo:**
- "Great question - let me finish the demo and I'll explain the architecture"
- Complete demo first, then deep dive

## Key Talking Points

✅ **Real vulnerabilities** - Not mock data, actual CVEs from NVD/OSV

✅ **Real fixes** - Actually queries PyPI for latest versions  

✅ **Real validation** - Tests dependency installation

✅ **Real PRs** - Creates actual GitHub pull requests

✅ **Fully autonomous** - No human in the loop

## Questions You'll Get

**Q: "How does it know which version to upgrade to?"**

A: "The Researcher agent queries the package registry—PyPI for Python, npm for JavaScript—and finds the latest stable version that doesn't have the CVE."

**Q: "What if the upgrade breaks something?"**

A: "The Validator agent tests the new dependencies in an isolated environment. If installation fails or tests break, it rejects the patch and can retry with a different version."

**Q: "Can it handle multiple CVEs at once?"**

A: "Yes! Scanner finds all vulnerabilities and prioritizes by CVSS score. We're showing one fix for demo clarity, but it can batch-process multiple patches."

**Q: "Why Nemotron specifically?"**

A: "Nemotron excels at function calling and multi-step reasoning—perfect for agents that need to use tools like GitHub API, NVD database, and package registries autonomously."

**Q: "Could this work in CI/CD?"**

A: "Absolutely. Run PatchForge as a scheduled job, and it automatically creates security PRs for your team to review and merge."

## Timing Breakdown

- Problem statement: 15 sec
- Demo setup: 15 sec  
- Agents running: 30 sec
- Show PR: 30 sec
- Impact statement: 15 sec
- Buffer: 15 sec

**Total: 2 minutes** (perfect for 3-min slot)

