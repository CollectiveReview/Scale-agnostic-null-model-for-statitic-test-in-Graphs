#!/usr/bin/env python3
"""
Main orchestration script for automated literature retrieval and PR creation.

This script coordinates the entire pipeline:
1. Search for relevant papers from multiple sources
2. Score papers using SciBERT embeddings
3. Analyze top papers using LLM
4. Create GitHub PR with literature suggestions
"""

import argparse
import logging
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.search_engine import MultiSourceSearchEngine
from modules.relevance_scorer import SciBERTRelevanceScorer, SimpleRelevanceScorer
from modules.llm_analyzer import LLMAnalyzer
from modules.github_integration import GitHubIntegration
from modules.config_manager import Config


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('literature_retrieval.log')
        ]
    )


class LiteratureRetrievalPipeline:
    """Main pipeline for automated literature retrieval."""
    
    def __init__(self, config: Config):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.search_engine = None
        self.relevance_scorer = None
        self.llm_analyzer = None
        self.github_integration = None
    
    def _init_search_engine(self):
        """Initialize search engine."""
        if self.search_engine is None:
            api_key = self.config.get('semantic_scholar.api_key')
            self.search_engine = MultiSourceSearchEngine(
                semantic_scholar_api_key=api_key
            )
            self.logger.info("Search engine initialized")
    
    def _init_relevance_scorer(self):
        """Initialize relevance scorer."""
        if self.relevance_scorer is None:
            scorer_type = self.config.get('relevance.scorer_type', 'simple')
            
            if scorer_type == 'scibert':
                try:
                    model_name = self.config.get('relevance.scibert_model', 'allenai/scibert_scivocab_uncased')
                    self.relevance_scorer = SciBERTRelevanceScorer(model_name=model_name)
                    self.logger.info("SciBERT relevance scorer initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize SciBERT scorer: {e}")
                    self.logger.info("Falling back to simple scorer")
                    self.relevance_scorer = SimpleRelevanceScorer()
            else:
                self.relevance_scorer = SimpleRelevanceScorer()
                self.logger.info("Simple relevance scorer initialized")
    
    def _init_llm_analyzer(self):
        """Initialize LLM analyzer if enabled."""
        if self.llm_analyzer is None and self.config.get('llm.enabled', False):
            provider = self.config.get('llm.provider', 'openai')
            model = self.config.get('llm.model')
            api_key = self.config.get('llm.api_key')
            
            if api_key:
                self.llm_analyzer = LLMAnalyzer(
                    provider=provider,
                    api_key=api_key,
                    model=model
                )
                self.logger.info(f"LLM analyzer initialized with {provider}")
            else:
                self.logger.warning("LLM API key not provided, LLM analysis disabled")
    
    def _init_github_integration(self):
        """Initialize GitHub integration."""
        if self.github_integration is None:
            repo_owner = self.config.get('github.repo_owner')
            repo_name = self.config.get('github.repo_name')
            github_token = self.config.get('github.github_token')
            base_branch = self.config.get('github.base_branch', 'main')
            
            if repo_owner and repo_name:
                self.github_integration = GitHubIntegration(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    github_token=github_token,
                    base_branch=base_branch
                )
                self.logger.info("GitHub integration initialized")
            else:
                self.logger.warning("GitHub configuration incomplete, PR creation disabled")
    
    def run(
        self,
        query: str,
        context: Optional[str] = None,
        create_pr: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete literature retrieval pipeline.
        
        Args:
            query: Search query for literature
            context: Optional research context for relevance scoring
            create_pr: Whether to create GitHub PR
            
        Returns:
            Dictionary with pipeline results
        """
        self.logger.info(f"Starting literature retrieval pipeline for query: {query}")
        
        results = {
            'query': query,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'papers': [],
            'scored_papers': [],
            'analyzed_papers': [],
            'pr_url': None
        }
        
        # Step 1: Search for papers
        self.logger.info("Step 1: Searching for papers...")
        self._init_search_engine()
        
        sources = self.config.get('search.sources', ['semantic_scholar', 'arxiv'])
        limit_per_source = self.config.get('search.limit_per_source', 10)
        
        papers = self.search_engine.search(
            query=query,
            limit_per_source=limit_per_source,
            sources=sources
        )
        
        # Deduplicate papers
        papers = self.search_engine.deduplicate_papers(papers)
        results['papers'] = [p.to_dict() for p in papers]
        
        self.logger.info(f"Found {len(papers)} unique papers")
        
        if not papers:
            self.logger.warning("No papers found, stopping pipeline")
            return results
        
        # Step 2: Score papers for relevance
        self.logger.info("Step 2: Scoring papers for relevance...")
        self._init_relevance_scorer()
        
        papers_dict = [p.to_dict() for p in papers]
        top_k = self.config.get('relevance.top_k', 10)
        
        scored_papers = self.relevance_scorer.score_papers(
            papers=papers_dict,
            query=query,
            context=context,
            top_k=top_k
        )
        
        results['scored_papers'] = [
            {'paper': paper, 'score': float(score)}
            for paper, score in scored_papers
        ]
        
        self.logger.info(f"Scored and filtered to top {len(scored_papers)} papers")
        
        # Step 3: Analyze papers with LLM (if enabled)
        if self.config.get('llm.enabled', False):
            self.logger.info("Step 3: Analyzing papers with LLM...")
            self._init_llm_analyzer()
            
            if self.llm_analyzer:
                max_analyze = self.config.get('llm.max_analyze', 5)
                analysis_type = self.config.get('llm.analysis_type', 'relevance')
                
                papers_to_analyze = [paper for paper, _ in scored_papers[:max_analyze]]
                
                analyzed_papers = self.llm_analyzer.batch_analyze_papers(
                    papers=papers_to_analyze,
                    context=context or query,
                    analysis_type=analysis_type
                )
                
                results['analyzed_papers'] = analyzed_papers
                self.logger.info(f"Analyzed {len(analyzed_papers)} papers with LLM")
            else:
                self.logger.info("LLM analyzer not available, skipping analysis")
                # Use scored papers as analyzed papers
                results['analyzed_papers'] = [
                    {'paper': paper, 'analysis': {'relevance_score': int(score * 10)}}
                    for paper, score in scored_papers
                ]
        else:
            self.logger.info("LLM analysis disabled, skipping")
            # Use scored papers as analyzed papers
            results['analyzed_papers'] = [
                {'paper': paper, 'analysis': {'relevance_score': int(score * 10)}}
                for paper, score in scored_papers
            ]
        
        # Step 4: Save results
        output_dir = self.config.get('general.output_dir', './literature_results')
        if self.config.get('general.save_results', True):
            self._save_results(results, output_dir)
        
        # Step 5: Create GitHub PR (if enabled)
        if create_pr and self.config.get('github.auto_create_pr', False):
            self.logger.info("Step 4: Creating GitHub pull request...")
            self._init_github_integration()
            
            if self.github_integration:
                pr_url = self.github_integration.create_literature_suggestion_pr(
                    papers=results['analyzed_papers'],
                    topic=query
                )
                
                if pr_url:
                    results['pr_url'] = pr_url
                    self.logger.info(f"Pull request created: {pr_url}")
                    
                    # Add labels
                    labels = self.config.get('github.labels', [])
                    if labels:
                        self.github_integration.add_labels_to_pr(pr_url, labels)
                    
                    # Add reviewers
                    reviewers = self.config.get('github.reviewers', [])
                    if reviewers:
                        self.github_integration.add_reviewers_to_pr(pr_url, reviewers)
                else:
                    self.logger.error("Failed to create pull request")
            else:
                self.logger.warning("GitHub integration not available, skipping PR creation")
        
        self.logger.info("Pipeline completed successfully")
        return results
    
    def _save_results(self, results: Dict[str, Any], output_dir: str):
        """Save pipeline results to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = results['query'].lower().replace(' ', '_')[:50]
        filename = f"{query_slug}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results saved to {filepath}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated Literature Retrieval and PR Creation System'
    )
    parser.add_argument(
        'query',
        type=str,
        help='Search query for literature'
    )
    parser.add_argument(
        '--context',
        type=str,
        default=None,
        help='Research context for relevance scoring'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration YAML file'
    )
    parser.add_argument(
        '--no-pr',
        action='store_true',
        help='Disable automatic PR creation'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Load configuration
    config = Config(config_path=args.config)
    
    # Override log level if specified
    if args.log_level:
        config.set('general.log_level', args.log_level)
    
    # Create and run pipeline
    pipeline = LiteratureRetrievalPipeline(config)
    
    try:
        results = pipeline.run(
            query=args.query,
            context=args.context,
            create_pr=not args.no_pr
        )
        
        # Print summary
        print("\n" + "="*80)
        print("PIPELINE RESULTS SUMMARY")
        print("="*80)
        print(f"Query: {results['query']}")
        print(f"Papers found: {len(results['papers'])}")
        print(f"Papers scored: {len(results['scored_papers'])}")
        print(f"Papers analyzed: {len(results['analyzed_papers'])}")
        
        if results['pr_url']:
            print(f"Pull Request: {results['pr_url']}")
        
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
