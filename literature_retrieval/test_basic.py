#!/usr/bin/env python3
"""
Simple test script to verify the literature retrieval system is working.
Tests each component in isolation without requiring API keys.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from modules.search_engine import MultiSourceSearchEngine, Paper
        from modules.relevance_scorer import SimpleRelevanceScorer
        from modules.llm_analyzer import LLMAnalyzer
        from modules.github_integration import GitHubIntegration
        from modules.config_manager import Config
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from modules.config_manager import Config
        config = Config()
        
        # Test getting values
        sources = config.get('search.sources', [])
        assert isinstance(sources, list), "Sources should be a list"
        
        # Test setting values
        config.set('test.value', 42)
        assert config.get('test.value') == 42, "Set/get should work"
        
        print("✓ Configuration system working")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_paper_dataclass():
    """Test Paper dataclass."""
    print("\nTesting Paper dataclass...")
    try:
        from modules.search_engine import Paper
        
        paper = Paper(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="This is a test abstract",
            year=2023,
            venue="Test Conference",
            url="https://example.com",
            doi="10.1234/test",
            citations=100,
            source="test"
        )
        
        # Test conversion to dict
        paper_dict = paper.to_dict()
        assert paper_dict['title'] == "Test Paper"
        assert len(paper_dict['authors']) == 2
        
        print("✓ Paper dataclass working")
        return True
    except Exception as e:
        print(f"✗ Paper dataclass error: {e}")
        return False


def test_simple_relevance_scorer():
    """Test simple relevance scorer (no dependencies)."""
    print("\nTesting simple relevance scorer...")
    try:
        from modules.relevance_scorer import SimpleRelevanceScorer
        
        scorer = SimpleRelevanceScorer()
        
        papers = [
            {
                'title': 'Machine Learning for Networks',
                'abstract': 'This paper discusses machine learning applications in network analysis',
                'authors': ['Author 1'],
                'year': 2023,
                'citations': 50
            },
            {
                'title': 'Deep Learning Methods',
                'abstract': 'A survey of deep learning techniques',
                'authors': ['Author 2'],
                'year': 2022,
                'citations': 100
            }
        ]
        
        scored = scorer.score_papers(
            papers=papers,
            query="machine learning networks",
            top_k=2
        )
        
        assert len(scored) == 2, "Should return 2 papers"
        assert scored[0][1] >= scored[1][1], "Should be sorted by score"
        
        print(f"✓ Simple scorer working (top score: {scored[0][1]:.3f})")
        return True
    except Exception as e:
        print(f"✗ Simple scorer error: {e}")
        return False


def test_search_engine_structure():
    """Test search engine structure (without making API calls)."""
    print("\nTesting search engine structure...")
    try:
        from modules.search_engine import MultiSourceSearchEngine, Paper
        
        engine = MultiSourceSearchEngine()
        
        # Test deduplication
        papers = [
            Paper(
                title="Same Paper",
                authors=["A"],
                abstract="Abstract",
                year=2023,
                venue="V",
                url="http://example.com",
                doi="10.1234/same",
                citations=10,
                source="source1"
            ),
            Paper(
                title="Same Paper",
                authors=["A"],
                abstract="Abstract",
                year=2023,
                venue="V",
                url="http://example.com",
                doi="10.1234/same",
                citations=10,
                source="source2"
            ),
            Paper(
                title="Different Paper",
                authors=["B"],
                abstract="Other",
                year=2023,
                venue="V",
                url="http://example.com/2",
                doi="10.1234/different",
                citations=5,
                source="source1"
            )
        ]
        
        unique = engine.deduplicate_papers(papers)
        assert len(unique) == 2, "Should deduplicate to 2 papers"
        
        print("✓ Search engine structure working")
        return True
    except Exception as e:
        print(f"✗ Search engine error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Literature Retrieval System - Basic Tests")
    print("="*60)
    
    tests = [
        test_imports,
        test_config,
        test_paper_dataclass,
        test_simple_relevance_scorer,
        test_search_engine_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✓ All basic tests passed!")
        print("\nNote: These tests verify structure only.")
        print("Full functionality requires API keys for:")
        print("  - Semantic Scholar, arXiv, CrossRef (search)")
        print("  - OpenAI or Anthropic (LLM analysis)")
        print("  - GitHub (PR creation)")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
