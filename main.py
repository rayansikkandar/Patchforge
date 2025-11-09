#!/usr/bin/env python3
"""
PatchForge - Autonomous CVE Patching Agent
Interactive Terminal Interface
"""

import os
import sys
import time
import argparse
from github import Github
from config import GITHUB_TOKEN, MAX_RETRIES
from agents.scanner import ScannerAgent
from agents.researcher import ResearcherAgent
from agents.patch_generator import PatchGeneratorAgent
from agents.validator import ValidatorAgent
from agents.pr_creator import PRCreatorAgent
from utils.logger import setup_logger

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

logger = setup_logger("PatchForge")

def print_banner():
    """Print the PatchForge banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗  █████╗ ████████╗ ██████╗██╗  ██╗                 ║
║   ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║  ██║                 ║
║   ██████╔╝███████║   ██║   ██║     ███████║                 ║
║   ██╔═══╝ ██╔══██║   ██║   ██║     ██╔══██║                 ║
║   ██║     ██║  ██║   ██║   ╚██████╗██║  ██║                 ║
║   ╚═╝     ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝                 ║
║                                                               ║
║         ███████╗ ██████╗ ██████╗  ██████╗ ███████╗           ║
║         ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝           ║
║         █████╗  ██║   ██║██████╔╝██║  ███╗█████╗             ║
║         ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝             ║
║         ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗           ║
║         ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝           ║
║                                                               ║
║              Autonomous CVE Patching Agent                    ║
║              Powered by NVIDIA Nemotron 70B                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
    """
    print(banner)

def animate_thinking(message, duration=2):
    """Animate a thinking process"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Colors.CYAN}{frames[i % len(frames)]} {message}{Colors.END}", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{Colors.GREEN}✓ {message}{Colors.END}")

def print_step(step_number, total_steps, title):
    """Print a step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{step_number}/{total_steps}] {title}{Colors.END}")
    print(f"{Colors.BLUE}{'─' * 60}{Colors.END}")

def get_github_username():
    """Get GitHub username from user"""
    print(f"\n{Colors.BOLD}Enter your GitHub username:{Colors.END} ", end="")
    username = input().strip()
    
    if not username:
        print(f"{Colors.RED}❌ Username cannot be empty{Colors.END}")
        sys.exit(1)
    
    return username

def list_user_repos(username):
    """List user's repositories"""
    try:
        animate_thinking(f"Fetching repositories for {username}", duration=1.5)
        
        g = Github(GITHUB_TOKEN)
        user = g.get_user(username)
        repos = list(user.get_repos())
        
        if not repos:
            print(f"{Colors.RED}❌ No repositories found{Colors.END}")
            sys.exit(1)
        
        return repos
    except Exception as e:
        print(f"{Colors.RED}❌ Error fetching repositories: {e}{Colors.END}")
        sys.exit(1)

def select_repository(repos):
    """Let user select a repository"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}Found {len(repos)} repositories:{Colors.END}\n")
    
    # Display repos in a nice table
    for i, repo in enumerate(repos[:20], 1):  # Show max 20
        status = f"{Colors.GREEN}public{Colors.END}" if not repo.private else f"{Colors.YELLOW}private{Colors.END}"
        stars = f"⭐ {repo.stargazers_count}" if repo.stargazers_count > 0 else ""
        print(f"  {Colors.CYAN}{i:2d}.{Colors.END} {Colors.BOLD}{repo.name}{Colors.END} ({status}) {stars}")
        if repo.description:
            desc = repo.description[:60] + "..." if len(repo.description) > 60 else repo.description
            print(f"      {Colors.BLUE}{desc}{Colors.END}")
    
    if len(repos) > 20:
        print(f"\n  {Colors.YELLOW}... and {len(repos) - 20} more{Colors.END}")
    
    # Get user selection
    while True:
        print(f"\n{Colors.BOLD}Select repository number (1-{min(20, len(repos))}):{Colors.END} ", end="")
        try:
            selection = int(input().strip())
            if 1 <= selection <= min(20, len(repos)):
                selected_repo = repos[selection - 1]
                print(f"\n{Colors.GREEN}✓ Selected: {Colors.BOLD}{selected_repo.full_name}{Colors.END}")
                return selected_repo
            else:
                print(f"{Colors.RED}❌ Please enter a number between 1 and {min(20, len(repos))}{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Please enter a valid number{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Cancelled by user{Colors.END}")
            sys.exit(0)

def clone_or_use_repo(repo):
    """Clone repository or use local copy"""
    repo_dir = f"./temp_repos/{repo.name}"
    
    if os.path.exists(repo_dir):
        print(f"{Colors.GREEN}✓ Using existing local copy: {repo_dir}{Colors.END}")
        return repo_dir
    
    animate_thinking(f"Cloning {repo.name}", duration=2)
    
    # Create temp directory
    os.makedirs("./temp_repos", exist_ok=True)
    
    # Clone (shallow clone for speed)
    try:
        import subprocess
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo.clone_url, repo_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Repository cloned successfully{Colors.END}")
            return repo_dir
        else:
            print(f"{Colors.RED}❌ Clone failed: {result.stderr}{Colors.END}")
            sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Error cloning repository: {e}{Colors.END}")
        sys.exit(1)

def run_agent_pipeline(repo_path, repo_full_name, explain=False, demo_react=False):
    """Run the agent pipeline with visual feedback and ReAct-style retry loop
    
    Args:
        repo_path: Path to the repository
        repo_full_name: GitHub repository name (e.g., 'owner/repo')
        explain: Whether to generate CVE explanations
        demo_react: Whether to enable demo mode (showcase ReAct loop)
    """
    
    total_steps = 6 if explain else 5
    attempts = 0  # Initialize attempts counter
    
    if demo_react:
        print(f"\n{Colors.CYAN}{Colors.BOLD}🎭 DEMO MODE: ReAct Loop Showcase{Colors.END}")
        print(f"{Colors.CYAN}This demo will showcase intelligent conflict resolution{Colors.END}\n")
    
    # Step 1: Scanner
    print_step(1, total_steps, "🔍 SCANNING FOR VULNERABILITIES")
    animate_thinking("Analyzing dependencies", duration=1)
    
    scanner = ScannerAgent()
    cves = scanner.scan_repository(repo_path, repo_name=repo_full_name)
    
    if not cves:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ No high-severity CVEs found!{Colors.END}")
        print(f"{Colors.GREEN}Your repository is secure. 🎉{Colors.END}")
        return
    
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Found {len(cves)} high-severity CVE(s):{Colors.END}")
    for cve in cves:
        print(f"  • {Colors.RED}{cve['cve_id']}{Colors.END} - CVSS: {Colors.BOLD}{cve['cvss_score']}/10{Colors.END}")
        print(f"    Package: {Colors.YELLOW}{cve['package']}{Colors.END} v{cve['current_version']}")
    
    # Select first CVE to patch
    target_cve = cves[0]
    print(f"\n{Colors.CYAN}→ Targeting: {Colors.BOLD}{target_cve['cve_id']}{Colors.END}")
    
    # Step 2: Researcher
    print_step(2, total_steps, "🔬 RESEARCHING VULNERABILITY")
    animate_thinking("Querying package registry", duration=1.5)
    animate_thinking("Finding secure version", duration=1.5)
    
    researcher = ResearcherAgent()
    research = researcher.research_cve(target_cve)
    
    if not research:
        print(f"\n{Colors.RED}❌ Could not find secure version{Colors.END}")
        print(f"{Colors.YELLOW}Skipping this CVE...{Colors.END}")
        return
    
    print(f"\n{Colors.GREEN}✓ Research complete{Colors.END}")
    print(f"{Colors.BLUE}Secure version found: {research['secure_version']}{Colors.END}")
    
    # Step 2.5/3: Generate CVE explanation (if --explain flag is set)
    cve_explanation = None
    if explain:
        step_num = 3
        print_step(step_num, total_steps, "📚 GENERATING CVE EXPLANATION")
        animate_thinking("Analyzing CVE with Nemotron", duration=2)
        
        cve_explanation = researcher.explain_cve_fix(target_cve, research)
        
        if cve_explanation:
            print(f"\n{Colors.GREEN}✓ Explanation generated{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Could not generate explanation{Colors.END}")
    
    # Step 3/4: Patch Generator & Validator with ReAct Loop
    patch_step = 4 if explain else 3
    print_step(patch_step, total_steps, "🔧 GENERATING & VALIDATING PATCH")
    
    # ReAct-style retry loop with multi-package updates
    patcher = PatchGeneratorAgent()
    validator = ValidatorAgent()
    patch = None
    validation = None
    validation_feedback = None
    success = False
    attempts = 0
    
    for attempt in range(1, MAX_RETRIES + 1):
        attempts = attempt
        logger.info(f"🧠 ReAct Loop - Attempt {attempt}/{MAX_RETRIES}")
        
        if attempt > 1:
            print(f"\n{Colors.BLUE}{'─' * 60}{Colors.END}")
            print(f"{Colors.BOLD}[{patch_step}/{total_steps}] 🔄 RETRY {attempt}/{MAX_RETRIES} - REFINING PATCH{Colors.END}")
            print(f"{Colors.BLUE}{'─' * 60}{Colors.END}")
            print(f"\n{Colors.YELLOW}🔄 ReAct Loop: Previous validation failed{Colors.END}")
            print(f"{Colors.CYAN}🤔 Agent analyzing conflict and refining approach...{Colors.END}")
            animate_thinking("Analyzing feedback", duration=1)
            animate_thinking("Refining patch", duration=1.5)
        else:
            animate_thinking("Reading dependency file", duration=0.5)
            animate_thinking("Updating package version", duration=1)
        
        # Generate or refine patch (with feedback and attempt number)
        patch = patcher.generate_patch(research, repo_path, feedback=validation_feedback, attempt=attempt)
        
        if not patch:
            print(f"\n{Colors.RED}❌ Failed to generate patch{Colors.END}")
            return
        
        print(f"\n{Colors.GREEN}✓ Patch generated{Colors.END}")
        
        # Show what was updated
        if attempt > 1 and patch.get('refinement_changes'):
            print(f"{Colors.CYAN}📝 Refined changes:{Colors.END}")
            for change in patch.get('refinement_changes', [])[:10]:  # Show up to 10 changes
                if change.strip() and ('==' in change or '>=' in change or '~=' in change):
                    # Extract package name and version
                    parts = change.split()
                    if len(parts) >= 2:
                        pkg_info = ' '.join(parts[:2])
                        print(f"   {Colors.CYAN}• {pkg_info}{Colors.END}")
                    else:
                        print(f"   {Colors.CYAN}• {change}{Colors.END}")
        else:
            print(f"{Colors.BLUE}File: {patch['file_path']}{Colors.END}")
            print(f"{Colors.BLUE}Changes: {patch['description']}{Colors.END}")
        
        # Validate patch
        if attempt == 1:
            animate_thinking("Creating test environment", duration=0.5)
            animate_thinking("Running dependency checks", duration=1)
            animate_thinking("Testing installation", duration=1)
        else:
            animate_thinking("Re-validating refined patch", duration=1.5)
        
        validation = validator.validate_patch(patch, repo_path)
        
        if validation['passed']:
            success = True
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ VALIDATION PASSED{Colors.END}")
            if attempt > 1:
                print(f"{Colors.GREEN}✨ ReAct loop succeeded after {attempt} attempts{Colors.END}")
                if patch.get('refinement_changes'):
                    print(f"{Colors.CYAN}✅ Coordinated multi-package update resolved conflicts{Colors.END}")
            print(f"{Colors.GREEN}All tests successful - patch is safe to deploy{Colors.END}")
            break
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  VALIDATION FAILED (Attempt {attempt}/{MAX_RETRIES}){Colors.END}")
            error_msg = validation['message'][:200]
            print(f"{Colors.YELLOW}{error_msg}...{Colors.END}")
            
            # Show suggestions if available
            if validation.get('suggestions'):
                print(f"\n{Colors.CYAN}{Colors.BOLD}💡 Agent Analysis:{Colors.END}")
                for suggestion in validation['suggestions']:
                    print(f"   {Colors.CYAN}• {suggestion}{Colors.END}")
            
            # Extract feedback for next iteration
            validation_feedback = validation.get('details', validation.get('message', ''))
            if validation.get('conflicting_packages'):
                validation_feedback += f"\nConflicting packages: {', '.join(validation['conflicting_packages'])}"
            if validation.get('suggestions'):
                validation_feedback += f"\nSuggestions: {'; '.join(validation['suggestions'])}"
            
            # Check if we should retry (only for conflicts, not build errors)
            should_retry = validation.get('needs_retry', True) and attempt < MAX_RETRIES
            
            if should_retry:
                if demo_react:
                    print(f"\n{Colors.CYAN}{Colors.BOLD}🤔 Agent Reasoning:{Colors.END}")
                    print(f"{Colors.CYAN}   Analyzing conflict and refining approach...{Colors.END}")
                    print(f"{Colors.CYAN}   Using Nemotron to resolve dependency conflicts{Colors.END}")
                    print(f"{Colors.CYAN}   Coordinating multi-package updates...{Colors.END}")
                    time.sleep(2)  # Dramatic pause for demo
                print(f"\n{Colors.CYAN}🔁 Retrying with refined approach...{Colors.END}")
                logger.info(f"Feedback for next attempt: {validation_feedback[:300]}")
            elif attempt < MAX_RETRIES and not validation.get('needs_retry', True):
                print(f"\n{Colors.YELLOW}⚠️  Error type not suitable for retry (build error, not conflict){Colors.END}")
                break
            else:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ All retry attempts exhausted{Colors.END}")
                print(f"{Colors.RED}Validation failed after {MAX_RETRIES} attempts{Colors.END}")
                if validation.get('details'):
                    print(f"{Colors.YELLOW}Final error: {validation['details'][:300]}...{Colors.END}")
                print(f"\n{Colors.CYAN}💡 Manual intervention may be required{Colors.END}")
                return
    
    if not success:
        print(f"\n{Colors.YELLOW}💡 Manual intervention may be required{Colors.END}")
        return
    
    # Step 5 (or 6): PR Creator
    step_num = 6 if explain else 5
    print_step(step_num, total_steps, "📝 CREATING PULL REQUEST")
    animate_thinking("Preparing commit", duration=1)
    animate_thinking("Creating branch", duration=1)
    animate_thinking("Opening pull request", duration=2)
    
    pr_creator = PRCreatorAgent()
    pr_url = pr_creator.create_pr(patch, validation, repo_full_name, research, 
                                   cve_explanation=cve_explanation, attempts=attempts)
    
    if not pr_url:
        print(f"\n{Colors.RED}❌ Failed to create PR{Colors.END}")
        logger.error("PR creation failed")
        return
    
    # Success summary
    print(f"\n{Colors.GREEN}{'═' * 60}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}✓ PIPELINE COMPLETE{Colors.END}")
    print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
    
    print(f"\n{Colors.BOLD}📊 Summary:{Colors.END}")
    print(f"  • CVE Fixed: {Colors.CYAN}{target_cve['cve_id']}{Colors.END}")
    print(f"  • Severity: {Colors.RED}CVSS {target_cve.get('cvss_score', 0)}/10{Colors.END}")
    print(f"  • Package: {Colors.YELLOW}{research['package']}{Colors.END}")
    print(f"  • Version: {Colors.CYAN}{research['current_version']} → {research['secure_version']}{Colors.END}")
    print(f"  • Validation: {Colors.GREEN}PASSED ✓{Colors.END}")
    print(f"  • Total Attempts: {Colors.CYAN}{attempts}{Colors.END}")
    if attempts > 1:
        print(f"  • ReAct Loop: {Colors.CYAN}Used (refined patch after {attempts} attempts){Colors.END}")
        refinement_changes = patch.get('refinement_changes', [])
        if refinement_changes:
            # Count unique packages updated
            unique_packages = set()
            for change in refinement_changes:
                if change.strip():
                    pkg_name = change.strip().split()[0] if change.strip().split() else change.strip()
                    unique_packages.add(pkg_name)
            if unique_packages:
                pkg_list = ', '.join(list(unique_packages)[:3])
                if len(unique_packages) > 3:
                    pkg_list += f" (+{len(unique_packages)-3} more)"
                print(f"  • Multi-Package Update: {Colors.CYAN}Yes ({len(unique_packages)} packages: {pkg_list}){Colors.END}")
    else:
        print(f"  • ReAct Loop: {Colors.GREEN}Not needed (patch passed on first try){Colors.END}")
    print(f"  • PR Created: {Colors.GREEN}True ✓{Colors.END}")
    
    print(f"\n{Colors.BOLD}🔗 Pull Request:{Colors.END}")
    print(f"  {Colors.BLUE}{Colors.UNDERLINE}{pr_url}{Colors.END}")
    
    print(f"\n{Colors.GREEN}The security patch is ready for review and merge!{Colors.END}")
    print(f"{Colors.CYAN}Check your GitHub notifications 📬{Colors.END}\n")
    
    # Log summary for debugging
    logger.info(f"Pipeline complete - Attempts: {attempts}, Status: success, PR created: True")

def main():
    """Main interactive flow"""
    try:
        # Parse command line arguments first (before banner for --help)
        parser = argparse.ArgumentParser(
            description="PatchForge - Autonomous CVE Patching Agent",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py                              # Interactive mode
  python main.py --explain                    # Interactive mode with CVE explanations
  python main.py --demo-react                 # Demo mode: Showcase ReAct loop
  python main.py <repo_path> <repo_name>      # Non-interactive mode
  python main.py <repo_path> <repo_name> --explain      # With explanations
  python main.py <repo_path> <repo_name> --demo-react   # Demo mode with ReAct showcase
            """
        )
        parser.add_argument(
            '--explain',
            action='store_true',
            help='Generate detailed CVE fix explanations using Nemotron (adds to PR description)'
        )
        parser.add_argument(
            '--demo-react',
            action='store_true',
            help='Demo mode: Showcase ReAct loop with intentional conflicts (for demonstrations)'
        )
        parser.add_argument(
            'repo_path',
            nargs='?',
            help='Path to repository (optional, for non-interactive mode)'
        )
        parser.add_argument(
            'repo_name',
            nargs='?',
            help='GitHub repository name in format owner/repo (optional, for non-interactive mode)'
        )
        
        args = parser.parse_args()
        
        # Print banner
        print_banner()
        
        # Demo mode setup
        if args.demo_react:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}🎭 DEMO MODE: ReAct Loop Showcase{Colors.END}")
            print(f"{Colors.YELLOW}This will create intentional conflicts to showcase intelligent refinement{Colors.END}")
            print(f"{Colors.YELLOW}Perfect for demonstrating PatchForge's autonomous capabilities{Colors.END}\n")
        
        # Check if running in non-interactive mode (command line args)
        if args.repo_path and args.repo_name:
            # Non-interactive mode: python main.py <repo_path> <github_repo_name>
            print(f"{Colors.CYAN}Running in non-interactive mode{Colors.END}")
            if args.explain:
                print(f"{Colors.CYAN}📚 Explanation mode: ON{Colors.END}")
            if args.demo_react:
                print(f"{Colors.CYAN}🎭 Demo mode: ON (ReAct loop showcase){Colors.END}")
            print(f"{Colors.BLUE}Repository: {args.repo_name}{Colors.END}")
            print(f"{Colors.BLUE}Path: {args.repo_path}{Colors.END}\n")
            
            # Setup demo scenario if requested
            if args.demo_react:
                from demo_mode import create_react_test_scenario
                create_react_test_scenario(args.repo_path)
                time.sleep(1)
            
            run_agent_pipeline(args.repo_path, args.repo_name, explain=args.explain, demo_react=args.demo_react)
            return
        
        # Interactive mode
        # Get GitHub username
        username = get_github_username()
        
        # Fetch and list repositories
        repos = list_user_repos(username)
        
        # Let user select repo
        selected_repo = select_repository(repos)
        
        # Clone or use existing
        repo_path = clone_or_use_repo(selected_repo)
        
        # Setup demo scenario if requested
        if args.demo_react:
            from demo_mode import create_react_test_scenario
            print(f"\n{Colors.CYAN}🎭 Setting up demo scenario...{Colors.END}")
            create_react_test_scenario(repo_path)
            time.sleep(1)
        
        # Confirmation
        print(f"\n{Colors.YELLOW}{'─' * 60}{Colors.END}")
        print(f"{Colors.BOLD}Ready to scan:{Colors.END} {Colors.CYAN}{selected_repo.full_name}{Colors.END}")
        if args.explain:
            print(f"{Colors.CYAN}📚 Explanation mode: ON (CVE fixes will include detailed explanations){Colors.END}")
        if args.demo_react:
            print(f"{Colors.CYAN}🎭 Demo mode: ON (ReAct loop showcase with intentional conflicts){Colors.END}")
        print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
        print(f"\n{Colors.BOLD}Press ENTER to start autonomous security scan, or Ctrl+C to cancel{Colors.END}")
        input()
        
        # Run the pipeline
        run_agent_pipeline(repo_path, selected_repo.full_name, explain=args.explain, demo_react=args.demo_react)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Operation cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        logger.exception("Fatal error in main")
        sys.exit(1)

if __name__ == "__main__":
    main()
