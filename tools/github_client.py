from github import Github, GithubException
from config import GITHUB_TOKEN
from utils.logger import setup_logger
from typing import Optional

logger = setup_logger("GitHub")

class GitHubClient:
    def __init__(self, token: str = GITHUB_TOKEN):
        self.client = Github(token)
        self.user = self.client.get_user()
    
    def create_pr(self, repo_name: str, title: str, body: str, 
                  head_branch: str, base_branch: str = "main") -> Optional[str]:
        """Create a pull request"""
        try:
            repo = self.client.get_repo(repo_name)
            
            # Create PR
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            logger.info(f"✅ PR created: {pr.html_url}")
            return pr.html_url
            
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            return None
    
    def create_branch(self, repo_name: str, branch_name: str, 
                     from_branch: str = "main") -> bool:
        """Create a new branch"""
        try:
            repo = self.client.get_repo(repo_name)
            source = repo.get_branch(from_branch)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            logger.info(f"Created branch: {branch_name}")
            return True
        except GithubException as e:
            logger.error(f"Error creating branch: {e}")
            return False
    
    def commit_file(self, repo_name: str, file_path: str, 
                   content: str, message: str, branch: str):
        """Commit a file to a branch"""
        try:
            repo = self.client.get_repo(repo_name)
            
            # Try to get existing file
            try:
                contents = repo.get_contents(file_path, ref=branch)
                repo.update_file(
                    contents.path,
                    message,
                    content,
                    contents.sha,
                    branch=branch
                )
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    file_path,
                    message,
                    content,
                    branch=branch
                )
            
            logger.info(f"Committed {file_path} to {branch}")
            return True
            
        except GithubException as e:
            logger.error(f"Error committing file: {e}")
            return False

