"""
GitHub integration module for automated PR creation.

This module handles creating pull requests to suggest new literature.
"""

import logging
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubIntegration:
    """
    GitHub integration for creating pull requests with literature suggestions.
    """
    
    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        github_token: Optional[str] = None,
        base_branch: str = "main"
    ):
        """
        Initialize GitHub integration.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: Repository name
            github_token: GitHub personal access token
            base_branch: Base branch for PRs
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.base_branch = base_branch
        self.github = None
    
    def _lazy_load_github(self):
        """Lazy load PyGithub client."""
        if self.github is None:
            try:
                from github import Github
                if not self.github_token:
                    raise ValueError("GitHub token not provided")
                self.github = Github(self.github_token)
                logger.info("GitHub client initialized")
            except ImportError:
                logger.error("PyGithub not installed. Install with: pip install PyGithub")
                raise
    
    def create_literature_suggestion_pr(
        self,
        papers: List[Dict[str, Any]],
        topic: str,
        branch_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a pull request suggesting new literature.
        
        Args:
            papers: List of paper dictionaries with analysis
            topic: Research topic
            branch_name: Custom branch name (auto-generated if None)
            
        Returns:
            URL of created pull request or None if failed
        """
        self._lazy_load_github()
        
        # Generate branch name
        if branch_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"literature-suggestion-{timestamp}"
        
        try:
            # Get repository
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            
            # Get base branch reference
            base_ref = repo.get_git_ref(f"heads/{self.base_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            new_ref = repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            logger.info(f"Created branch: {branch_name}")
            
            # Create literature file
            literature_content = self._generate_literature_file(papers, topic)
            file_path = f"related_research/{topic.lower().replace(' ', '_')}.md"
            
            # Create or update file
            try:
                # Try to get existing file
                existing_file = repo.get_contents(file_path, ref=branch_name)
                repo.update_file(
                    path=file_path,
                    message=f"Add literature suggestions for {topic}",
                    content=literature_content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
            except Exception as e:
                # File doesn't exist, create it
                logger.debug(f"File doesn't exist, creating new: {e}")
                repo.create_file(
                    path=file_path,
                    message=f"Add literature suggestions for {topic}",
                    content=literature_content,
                    branch=branch_name
                )
            
            logger.info(f"Created file: {file_path}")
            
            # Create pull request
            pr_title = f"Literature Suggestion: {topic}"
            pr_body = self._generate_pr_description(papers, topic)
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=self.base_branch
            )
            
            logger.info(f"Created PR: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def _generate_literature_file(
        self,
        papers: List[Dict[str, Any]],
        topic: str
    ) -> str:
        """
        Generate markdown content for literature file.
        
        Args:
            papers: List of papers with analysis
            topic: Research topic
            
        Returns:
            Markdown content
        """
        content = f"# Literature Review: {topic}\n\n"
        content += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        content += "## Overview\n\n"
        content += f"This document contains {len(papers)} relevant papers for the topic: {topic}\n\n"
        content += "## Papers\n\n"
        
        for i, item in enumerate(papers, 1):
            paper = item.get("paper", item)
            analysis = item.get("analysis", {})
            
            content += f"### {i}. {paper.get('title', 'Unknown Title')}\n\n"
            
            # Authors
            authors = paper.get('authors', [])
            if authors:
                content += f"**Authors:** {', '.join(authors[:5])}"
                if len(authors) > 5:
                    content += f" et al."
                content += "\n\n"
            
            # Metadata
            year = paper.get('year')
            venue = paper.get('venue')
            citations = paper.get('citations')
            
            metadata = []
            if year:
                metadata.append(f"**Year:** {year}")
            if venue:
                metadata.append(f"**Venue:** {venue}")
            if citations is not None:
                metadata.append(f"**Citations:** {citations}")
            
            if metadata:
                content += " | ".join(metadata) + "\n\n"
            
            # Links
            links = []
            if paper.get('url'):
                links.append(f"[Paper]({paper['url']})")
            if paper.get('pdf_url'):
                links.append(f"[PDF]({paper['pdf_url']})")
            if paper.get('doi'):
                links.append(f"[DOI](https://doi.org/{paper['doi']})")
            
            if links:
                content += "**Links:** " + " | ".join(links) + "\n\n"
            
            # Abstract
            abstract = paper.get('abstract', '')
            if abstract:
                content += f"**Abstract:** {abstract[:500]}"
                if len(abstract) > 500:
                    content += "..."
                content += "\n\n"
            
            # Analysis
            if analysis:
                relevance_score = analysis.get('relevance_score')
                if relevance_score:
                    content += f"**Relevance Score:** {relevance_score}/10\n\n"
                
                key_contributions = analysis.get('key_contributions')
                if key_contributions:
                    content += "**Key Contributions:**\n"
                    if isinstance(key_contributions, list):
                        for contrib in key_contributions:
                            content += f"- {contrib}\n"
                    else:
                        content += f"{key_contributions}\n"
                    content += "\n"
                
                keywords = analysis.get('keywords')
                if keywords:
                    if isinstance(keywords, list):
                        content += f"**Keywords:** {', '.join(keywords)}\n\n"
                    else:
                        content += f"**Keywords:** {keywords}\n\n"
            
            content += "---\n\n"
        
        return content
    
    def _generate_pr_description(
        self,
        papers: List[Dict[str, Any]],
        topic: str
    ) -> str:
        """
        Generate pull request description.
        
        Args:
            papers: List of papers
            topic: Research topic
            
        Returns:
            PR description text
        """
        description = f"## Literature Suggestion for: {topic}\n\n"
        description += "This PR adds literature suggestions automatically retrieved and analyzed.\n\n"
        description += f"### Summary\n\n"
        description += f"- **Topic:** {topic}\n"
        description += f"- **Papers Found:** {len(papers)}\n"
        description += f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        
        description += "### Top Papers\n\n"
        for i, item in enumerate(papers[:5], 1):
            paper = item.get("paper", item)
            analysis = item.get("analysis", {})
            
            title = paper.get('title', 'Unknown')
            authors = paper.get('authors', [])
            author_str = authors[0] if authors else 'Unknown'
            if len(authors) > 1:
                author_str += " et al."
            
            year = paper.get('year', 'N/A')
            relevance = analysis.get('relevance_score', 'N/A')
            
            description += f"{i}. **{title}** - {author_str} ({year})"
            if relevance != 'N/A':
                description += f" - Relevance: {relevance}/10"
            description += "\n"
        
        description += "\n### Review Process\n\n"
        description += "This literature was:\n"
        description += "1. Retrieved from multiple academic sources (Semantic Scholar, arXiv, CrossRef)\n"
        description += "2. Scored for relevance using SciBERT embeddings\n"
        description += "3. Analyzed using LLM for quality and fit\n"
        description += "4. Automatically formatted for inclusion\n\n"
        
        description += "Please review the suggested papers and merge if appropriate.\n"
        
        return description
    
    def add_labels_to_pr(self, pr_url: str, labels: List[str]):
        """
        Add labels to a pull request.
        
        Args:
            pr_url: URL of the pull request
            labels: List of label names
        """
        self._lazy_load_github()
        
        try:
            # Extract PR number from URL
            pr_number = int(pr_url.split('/')[-1])
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            pr = repo.get_pull(pr_number)
            pr.add_to_labels(*labels)
            logger.info(f"Added labels {labels} to PR #{pr_number}")
        except Exception as e:
            logger.error(f"Error adding labels: {e}")
    
    def add_reviewers_to_pr(self, pr_url: str, reviewers: List[str]):
        """
        Add reviewers to a pull request.
        
        Args:
            pr_url: URL of the pull request
            reviewers: List of GitHub usernames
        """
        self._lazy_load_github()
        
        try:
            pr_number = int(pr_url.split('/')[-1])
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            pr = repo.get_pull(pr_number)
            pr.create_review_request(reviewers=reviewers)
            logger.info(f"Added reviewers {reviewers} to PR #{pr_number}")
        except Exception as e:
            logger.error(f"Error adding reviewers: {e}")
