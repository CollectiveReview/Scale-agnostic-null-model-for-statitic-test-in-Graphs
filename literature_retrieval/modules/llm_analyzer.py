"""
LLM-based paper analysis and summarization module.

This module uses LLM APIs (OpenAI, Anthropic, etc.) to analyze papers
and generate summaries and relevance assessments.
"""

import logging
from typing import List, Dict, Optional, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """
    LLM-based paper analyzer using various API providers.
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM analyzer.
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = provider.lower()
        self.api_key = api_key
        
        # Set default models
        if model is None:
            if self.provider == "openai":
                self.model = "gpt-4-turbo-preview"
            elif self.provider == "anthropic":
                self.model = "claude-3-sonnet-20240229"
            else:
                self.model = "gpt-3.5-turbo"
        else:
            self.model = model
        
        self.client = None
    
    def _lazy_load_client(self):
        """Lazy load the API client."""
        if self.client is None:
            if self.provider == "openai":
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized")
                except ImportError:
                    logger.error("openai package not installed. Install with: pip install openai")
                    raise
            elif self.provider == "anthropic":
                try:
                    from anthropic import Anthropic
                    self.client = Anthropic(api_key=self.api_key)
                    logger.info("Anthropic client initialized")
                except ImportError:
                    logger.error("anthropic package not installed. Install with: pip install anthropic")
                    raise
            else:
                logger.warning(f"Unknown provider: {self.provider}, using mock mode")
    
    def analyze_paper(
        self,
        paper: Dict[str, Any],
        context: str,
        analysis_type: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Analyze a paper using LLM.
        
        Args:
            paper: Paper dictionary
            context: Research context or topic
            analysis_type: Type of analysis (relevance, summary, critique)
            
        Returns:
            Analysis results as dictionary
        """
        self._lazy_load_client()
        
        # Prepare prompt based on analysis type
        if analysis_type == "relevance":
            prompt = self._create_relevance_prompt(paper, context)
        elif analysis_type == "summary":
            prompt = self._create_summary_prompt(paper)
        elif analysis_type == "critique":
            prompt = self._create_critique_prompt(paper, context)
        else:
            prompt = self._create_general_prompt(paper, context)
        
        # Call LLM
        try:
            response = self._call_llm(prompt)
            return self._parse_analysis_response(response, analysis_type)
        except Exception as e:
            logger.error(f"Error analyzing paper: {e}")
            return {"error": str(e)}
    
    def _create_relevance_prompt(self, paper: Dict[str, Any], context: str) -> str:
        """Create prompt for relevance analysis."""
        return f"""Analyze the relevance of this research paper to the given context.

Context: {context}

Paper Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Year: {paper.get('year', 'N/A')}
Venue: {paper.get('venue', 'N/A')}

Please provide:
1. Relevance score (0-10): How relevant is this paper to the context?
2. Key contributions: What are the main contributions of this paper?
3. Relevance explanation: Why is this paper relevant (or not relevant)?
4. Keywords: 5-7 keywords that describe this paper

Format your response as JSON with keys: relevance_score, key_contributions, relevance_explanation, keywords
"""
    
    def _create_summary_prompt(self, paper: Dict[str, Any]) -> str:
        """Create prompt for paper summary."""
        return f"""Summarize this research paper concisely.

Paper Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}
Year: {paper.get('year', 'N/A')}

Please provide:
1. One-sentence summary: A concise one-sentence description
2. Key findings: Main findings or contributions (3-5 bullet points)
3. Methodology: Brief description of the methodology used
4. Impact: Potential impact or significance of this work

Format your response as JSON with keys: one_sentence_summary, key_findings, methodology, impact
"""
    
    def _create_critique_prompt(self, paper: Dict[str, Any], context: str) -> str:
        """Create prompt for critical analysis."""
        return f"""Provide a critical analysis of this research paper in the context of: {context}

Paper Title: {paper.get('title', 'N/A')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', 'N/A')}

Please provide:
1. Strengths: What are the main strengths? (2-3 points)
2. Limitations: What are potential limitations or weaknesses? (2-3 points)
3. Future work: What future research directions does this suggest?
4. Recommendation: Should this paper be included in the literature review? (yes/no with brief explanation)

Format your response as JSON with keys: strengths, limitations, future_work, recommendation
"""
    
    def _create_general_prompt(self, paper: Dict[str, Any], context: str) -> str:
        """Create general analysis prompt."""
        return f"""Analyze this research paper in the context of: {context}

Paper Title: {paper.get('title', 'N/A')}
Abstract: {paper.get('abstract', 'N/A')}

Provide a brief analysis of how this paper relates to the given context.
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        if self.client is None:
            # Mock response when no client available
            logger.warning("No LLM client available, returning mock response")
            return json.dumps({
                "relevance_score": 7,
                "key_contributions": ["Contribution 1", "Contribution 2"],
                "relevance_explanation": "This paper is relevant to the context.",
                "keywords": ["keyword1", "keyword2", "keyword3"]
            })
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert research analyst specializing in academic literature review."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            raise
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            # Try to parse as JSON
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Return raw text if not JSON
            logger.warning("Could not parse LLM response as JSON, returning raw text")
            return {"raw_response": response}
    
    def batch_analyze_papers(
        self,
        papers: List[Dict[str, Any]],
        context: str,
        analysis_type: str = "relevance",
        max_papers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple papers in batch.
        
        Args:
            papers: List of paper dictionaries
            context: Research context
            analysis_type: Type of analysis
            max_papers: Maximum number of papers to analyze
            
        Returns:
            List of analysis results
        """
        if max_papers is not None:
            papers = papers[:max_papers]
        
        results = []
        for i, paper in enumerate(papers):
            logger.info(f"Analyzing paper {i+1}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}...")
            analysis = self.analyze_paper(paper, context, analysis_type)
            results.append({
                "paper": paper,
                "analysis": analysis
            })
        
        return results
    
    def generate_literature_review(
        self,
        papers_with_analysis: List[Dict[str, Any]],
        context: str
    ) -> str:
        """
        Generate a literature review section from analyzed papers.
        
        Args:
            papers_with_analysis: List of papers with their analyses
            context: Research context
            
        Returns:
            Literature review text
        """
        self._lazy_load_client()
        
        # Prepare papers summary
        papers_summary = []
        for item in papers_with_analysis[:10]:  # Limit to top 10 papers
            paper = item["paper"]
            analysis = item.get("analysis", {})
            papers_summary.append({
                "title": paper.get("title"),
                "authors": paper.get("authors"),
                "year": paper.get("year"),
                "relevance_score": analysis.get("relevance_score"),
                "key_contributions": analysis.get("key_contributions")
            })
        
        prompt = f"""Generate a literature review section based on these papers for the topic: {context}

Papers:
{json.dumps(papers_summary, indent=2)}

Please write a cohesive literature review that:
1. Groups papers by theme or approach
2. Highlights key contributions and findings
3. Identifies research gaps or opportunities
4. Maintains academic tone and proper citations

Keep it concise (300-500 words).
"""
        
        try:
            review = self._call_llm(prompt)
            return review
        except Exception as e:
            logger.error(f"Error generating literature review: {e}")
            return f"Error generating review: {str(e)}"
