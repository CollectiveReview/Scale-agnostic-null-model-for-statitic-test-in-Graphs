"""
Multi-source literature search engine module.

This module implements literature retrieval from multiple academic sources
including Semantic Scholar, arXiv, and CrossRef APIs.
"""

import requests
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Data class representing a research paper."""
    title: str
    authors: List[str]
    abstract: str
    year: Optional[int]
    venue: Optional[str]
    url: Optional[str]
    doi: Optional[str]
    citations: Optional[int]
    source: str  # semantic_scholar, arxiv, crossref
    pdf_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SemanticScholarSearch:
    """Search engine for Semantic Scholar API."""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
    
    def search(self, query: str, limit: int = 10, fields: Optional[List[str]] = None) -> List[Paper]:
        """
        Search for papers using Semantic Scholar API.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            fields: List of fields to retrieve
            
        Returns:
            List of Paper objects
        """
        if fields is None:
            fields = ["title", "authors", "abstract", "year", "venue", "url", 
                     "citationCount", "externalIds", "openAccessPdf"]
        
        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields)
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("data", []):
                authors = [author.get("name", "") for author in item.get("authors", [])]
                external_ids = item.get("externalIds", {})
                doi = external_ids.get("DOI") if external_ids else None
                
                pdf_url = None
                if item.get("openAccessPdf"):
                    pdf_url = item["openAccessPdf"].get("url")
                
                paper = Paper(
                    title=item.get("title", ""),
                    authors=authors,
                    abstract=item.get("abstract", ""),
                    year=item.get("year"),
                    venue=item.get("venue"),
                    url=item.get("url"),
                    doi=doi,
                    citations=item.get("citationCount"),
                    source="semantic_scholar",
                    pdf_url=pdf_url
                )
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from Semantic Scholar")
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []


class ArXivSearch:
    """Search engine for arXiv API."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """
        Search for papers using arXiv API.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of Paper objects
        """
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Define namespaces
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns)
                abstract = entry.find('atom:summary', ns)
                published = entry.find('atom:published', ns)
                url = entry.find('atom:id', ns)
                
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                
                # Extract year from published date
                year = None
                if published is not None and published.text:
                    year = int(published.text[:4])
                
                # Get PDF URL
                pdf_url = None
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href')
                        break
                
                paper = Paper(
                    title=title.text.strip() if title is not None else "",
                    authors=authors,
                    abstract=abstract.text.strip() if abstract is not None else "",
                    year=year,
                    venue="arXiv",
                    url=url.text if url is not None else None,
                    doi=None,
                    citations=None,
                    source="arxiv",
                    pdf_url=pdf_url
                )
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from arXiv")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []


class CrossRefSearch:
    """Search engine for CrossRef API."""
    
    BASE_URL = "https://api.crossref.org/works"
    
    def search(self, query: str, limit: int = 10) -> List[Paper]:
        """
        Search for papers using CrossRef API.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of Paper objects
        """
        params = {
            "query": query,
            "rows": limit,
            "select": "title,author,abstract,published,DOI,URL,container-title,is-referenced-by-count"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("message", {}).get("items", []):
                # Extract title
                title_list = item.get("title", [])
                title = title_list[0] if title_list else ""
                
                # Extract authors
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)
                
                # Extract year
                year = None
                published = item.get("published") or item.get("published-print") or item.get("published-online")
                if published and "date-parts" in published:
                    date_parts = published["date-parts"][0]
                    if date_parts:
                        year = date_parts[0]
                
                # Extract venue
                venue_list = item.get("container-title", [])
                venue = venue_list[0] if venue_list else None
                
                paper = Paper(
                    title=title,
                    authors=authors,
                    abstract=item.get("abstract", ""),
                    year=year,
                    venue=venue,
                    url=item.get("URL"),
                    doi=item.get("DOI"),
                    citations=item.get("is-referenced-by-count"),
                    source="crossref",
                    pdf_url=None
                )
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from CrossRef")
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching CrossRef: {e}")
            return []


class MultiSourceSearchEngine:
    """
    Unified search engine that queries multiple academic sources.
    """
    
    def __init__(self, semantic_scholar_api_key: Optional[str] = None):
        self.semantic_scholar = SemanticScholarSearch(api_key=semantic_scholar_api_key)
        self.arxiv = ArXivSearch()
        self.crossref = CrossRefSearch()
    
    def search(
        self,
        query: str,
        limit_per_source: int = 10,
        sources: Optional[List[str]] = None
    ) -> List[Paper]:
        """
        Search across multiple sources and return aggregated results.
        
        Args:
            query: Search query string
            limit_per_source: Maximum results per source
            sources: List of sources to search (default: all)
            
        Returns:
            List of Paper objects from all sources
        """
        if sources is None:
            sources = ["semantic_scholar", "arxiv", "crossref"]
        
        all_papers = []
        
        if "semantic_scholar" in sources:
            papers = self.semantic_scholar.search(query, limit=limit_per_source)
            all_papers.extend(papers)
            time.sleep(1)  # Rate limiting
        
        if "arxiv" in sources:
            papers = self.arxiv.search(query, limit=limit_per_source)
            all_papers.extend(papers)
            time.sleep(1)  # Rate limiting
        
        if "crossref" in sources:
            papers = self.crossref.search(query, limit=limit_per_source)
            all_papers.extend(papers)
            time.sleep(1)  # Rate limiting
        
        logger.info(f"Total papers found across all sources: {len(all_papers)}")
        return all_papers
    
    def deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Remove duplicate papers based on title similarity and DOI.
        
        Args:
            papers: List of papers to deduplicate
            
        Returns:
            Deduplicated list of papers
        """
        seen_dois = set()
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            # Check DOI first
            if paper.doi and paper.doi in seen_dois:
                continue
            
            # Check title (normalized)
            normalized_title = paper.title.lower().strip()
            if normalized_title in seen_titles:
                continue
            
            # Add to unique set
            if paper.doi:
                seen_dois.add(paper.doi)
            seen_titles.add(normalized_title)
            unique_papers.append(paper)
        
        logger.info(f"Deduplicated {len(papers)} papers to {len(unique_papers)}")
        return unique_papers
