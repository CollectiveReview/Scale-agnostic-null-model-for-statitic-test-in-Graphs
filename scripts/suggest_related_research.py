#!/usr/bin/env python3
"""
Citation Context Bot - Automatically suggests related research for new papers
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text by finding significant words."""
    # Remove markdown formatting
    text = re.sub(r'[#*`]', '', text)
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    # Filter common words
    stopwords = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'are', 'was', 'for', 'and', 'the', 'to', 'of', 'in', 'a', 'is', 'it', 'as', 'on', 'by'}
    keywords = [w for w in words if w not in stopwords]
    return keywords


def read_paper_content(filepath: Path) -> str:
    """Read the content of a paper file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return ""


def find_related_research(paper_content: str, related_research_dir: Path) -> List[Tuple[str, float]]:
    """
    Find related research based on keyword matching.
    
    Returns a list of tuples (filename, relevance_score) sorted by relevance.
    """
    if not related_research_dir.exists():
        return []
    
    paper_keywords = extract_keywords(paper_content)
    if not paper_keywords:
        return []
    
    paper_keyword_counts = Counter(paper_keywords)
    
    research_scores = []
    
    for research_file in related_research_dir.glob("*.md"):
        if research_file.name == "README.md":
            continue
        
        research_content = read_paper_content(research_file)
        research_keywords = extract_keywords(research_content)
        
        # Calculate relevance score based on common keywords
        common_keywords = set(paper_keywords) & set(research_keywords)
        if common_keywords:
            # Weight by frequency in both documents
            score = sum(paper_keyword_counts[kw] for kw in common_keywords)
            research_scores.append((research_file.name, score))
    
    # Sort by score (highest first)
    research_scores.sort(key=lambda x: x[1], reverse=True)
    
    return research_scores


def generate_related_work_section(related_files: List[Tuple[str, float]], related_research_dir: Path, max_items: int = 5) -> str:
    """Generate the Related Work section content."""
    if not related_files:
        return "\n## Related Work\n\n(No related research found yet)\n"
    
    section = "\n## Related Work\n\n"
    section += "The following related research has been automatically identified:\n\n"
    
    for filename, score in related_files[:max_items]:
        filepath = related_research_dir / filename
        content = read_paper_content(filepath)
        
        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else filename.replace('.md', '')
        
        # Extract year
        year_match = re.search(r'\*\*Year:\*\*\s*(\d{4})', content)
        year = year_match.group(1) if year_match else "N/A"
        
        # Extract authors
        authors_match = re.search(r'\*\*Authors:\*\*\s*(.+)$', content, re.MULTILINE)
        authors = authors_match.group(1).strip() if authors_match else "Unknown"
        
        section += f"### {title}\n\n"
        section += f"- **Authors:** {authors}\n"
        section += f"- **Year:** {year}\n"
        section += f"- **Reference:** `related_research/{filename}`\n\n"
    
    return section


def update_paper_with_related_work(paper_filepath: Path, related_research_dir: Path) -> bool:
    """
    Update a paper file with related work suggestions.
    
    Returns True if the file was modified, False otherwise.
    """
    content = read_paper_content(paper_filepath)
    if not content:
        return False
    
    # Check if Related Work section already exists
    if re.search(r'^##\s+Related Work', content, re.MULTILINE | re.IGNORECASE):
        print(f"Paper {paper_filepath.name} already has a Related Work section.")
        return False
    
    # Find related research
    related_files = find_related_research(content, related_research_dir)
    
    if not related_files:
        print(f"No related research found for {paper_filepath.name}")
        # Still add an empty section
    
    # Generate Related Work section
    related_work_section = generate_related_work_section(related_files, related_research_dir)
    
    # Add the section at the end of the file
    updated_content = content.rstrip() + "\n" + related_work_section
    
    # Write back to file
    try:
        with open(paper_filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated {paper_filepath.name} with {len(related_files)} related research items")
        return True
    except Exception as e:
        print(f"Error writing to {paper_filepath}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to process new or modified papers."""
    if len(sys.argv) < 2:
        print("Usage: python suggest_related_research.py <paper_file>")
        sys.exit(1)
    
    paper_file = sys.argv[1]
    paper_path = Path(paper_file)
    
    if not paper_path.exists():
        print(f"Error: Paper file {paper_file} not found")
        sys.exit(1)
    
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    related_research_dir = repo_root / "related_research"
    
    if not related_research_dir.exists():
        print(f"Warning: related_research directory not found at {related_research_dir}")
        related_research_dir.mkdir(exist_ok=True)
    
    # Process the paper
    modified = update_paper_with_related_work(paper_path, related_research_dir)
    
    if modified:
        print(f"Successfully updated {paper_file}")
        sys.exit(0)
    else:
        print(f"No changes made to {paper_file}")
        sys.exit(0)


if __name__ == "__main__":
    main()
