# Automated Literature Retrieval System

An automated pipeline for discovering, analyzing, and suggesting relevant academic literature using state-of-the-art NLP and information retrieval techniques.

## Features

- **Multi-Source Search**: Retrieves papers from multiple academic databases:
  - Semantic Scholar API
  - arXiv API  
  - CrossRef API
  
- **SciBERT-Based Relevance Scoring**: Uses SciBERT embeddings to compute semantic similarity and rank papers by relevance

- **LLM-Powered Analysis**: Leverages large language models (OpenAI GPT-4, Anthropic Claude) to:
  - Assess paper relevance
  - Extract key contributions
  - Generate summaries
  - Identify research gaps

- **Automated GitHub Integration**: Creates pull requests with formatted literature suggestions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
cd literature_retrieval
pip install -r requirements.txt
```

### Optional: Install with GPU support for SciBERT

For faster SciBERT inference with CUDA:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Configuration

### Environment Variables

Set the following environment variables for API access:

```bash
# Optional: Semantic Scholar API key (for higher rate limits)
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# Optional: OpenAI API key (for LLM analysis)
export OPENAI_API_KEY="your-api-key"

# Optional: Anthropic API key (alternative to OpenAI)
export ANTHROPIC_API_KEY="your-api-key"

# Required for PR creation: GitHub personal access token
export GITHUB_TOKEN="your-github-token"
```

### Configuration File

Edit `config/default_config.yaml` to customize the pipeline behavior:

```yaml
search:
  sources:
    - semantic_scholar
    - arxiv
    - crossref
  limit_per_source: 10

relevance:
  scorer_type: scibert  # or 'simple' for keyword-based
  top_k: 10

llm:
  enabled: true
  provider: openai  # or 'anthropic'
  model: gpt-4-turbo-preview

github:
  auto_create_pr: true
  repo_owner: YourOrg
  repo_name: YourRepo
```

## Usage

### Basic Usage

Search for literature on a topic:

```bash
python main.py "citation context analysis in scientific papers"
```

### With Context

Provide additional context for better relevance scoring:

```bash
python main.py "graph neural networks" \
  --context "Application to citation networks and bibliometric analysis"
```

### Custom Configuration

Use a custom configuration file:

```bash
python main.py "your query" --config path/to/config.yaml
```

### Disable PR Creation

Run search and analysis without creating a PR:

```bash
python main.py "your query" --no-pr
```

### Advanced Options

```bash
python main.py --help

usage: main.py [-h] [--context CONTEXT] [--config CONFIG] [--no-pr]
               [--log-level {DEBUG,INFO,WARNING,ERROR}]
               query

Automated Literature Retrieval and PR Creation System

positional arguments:
  query                 Search query for literature

optional arguments:
  -h, --help            show this help message and exit
  --context CONTEXT     Research context for relevance scoring
  --config CONFIG       Path to configuration YAML file
  --no-pr               Disable automatic PR creation
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level
```

## Pipeline Architecture

The system follows a multi-stage pipeline:

```
┌─────────────────────┐
│  Search Query       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Multi-Source       │
│  Literature Search  │
│  - Semantic Scholar │
│  - arXiv            │
│  - CrossRef         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Deduplication      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SciBERT Relevance  │
│  Scoring            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLM Analysis       │
│  (Top-K Papers)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  GitHub PR Creation │
│  (Formatted)        │
└─────────────────────┘
```

## Modules

### `search_engine.py`
Multi-source literature search with support for:
- Semantic Scholar API (comprehensive metadata)
- arXiv API (preprints)
- CrossRef API (published works)

### `relevance_scorer.py`
SciBERT-based semantic similarity scoring:
- Uses `allenai/scibert_scivocab_uncased` model
- Computes cosine similarity between query and paper embeddings
- Includes fallback to simple keyword-based scoring

### `llm_analyzer.py`
LLM-powered paper analysis:
- Supports OpenAI and Anthropic APIs
- Generates structured analysis (relevance, contributions, summaries)
- Batch processing with rate limiting

### `github_integration.py`
Automated PR creation:
- Creates formatted markdown literature files
- Generates descriptive PR descriptions
- Supports labels and reviewer assignment

### `config_manager.py`
Configuration management:
- YAML-based configuration
- Environment variable overrides
- Validation and defaults

## Example Output

When a PR is created, it includes:

### Literature File (`related_research/topic_name.md`)

```markdown
# Literature Review: Citation Context Analysis

*Generated on 2025-11-22*

## Papers

### 1. SciBERT: A Pretrained Language Model for Scientific Text

**Authors:** Beltagy, I., Lo, K., Cohan, A.

**Year:** 2019 | **Venue:** EMNLP | **Citations:** 2847

**Links:** [Paper](https://...) | [PDF](https://...)

**Abstract:** Scientific documents are different from general text...

**Relevance Score:** 9/10

**Key Contributions:**
- Pretrained BERT model on scientific corpus
- Improved performance on scientific NLP tasks

**Keywords:** scientific text, language models, BERT, NLP

---
```

### Pull Request Description

```markdown
## Literature Suggestion for: Citation Context Analysis

This PR adds literature suggestions automatically retrieved and analyzed.

### Summary

- **Topic:** Citation Context Analysis
- **Papers Found:** 15
- **Generated:** 2025-11-22 10:30:00 UTC

### Top Papers

1. **SciBERT: A Pretrained Language Model** - Beltagy et al. (2019) - Relevance: 9/10
2. **CiteBERT: Citation Context Analysis** - Smith et al. (2020) - Relevance: 8/10
...

### Review Process

This literature was:
1. Retrieved from multiple academic sources
2. Scored for relevance using SciBERT embeddings
3. Analyzed using LLM for quality and fit
4. Automatically formatted for inclusion

Please review the suggested papers and merge if appropriate.
```

## Research Background

This system is based on current research in automated literature retrieval:

- **Semantic Search**: Uses dense embeddings (SciBERT) for semantic similarity vs. traditional keyword matching
- **Multi-Source Aggregation**: Combines results from multiple databases to improve coverage
- **LLM-Assisted Analysis**: Leverages large language models for nuanced relevance assessment
- **Automation**: Reduces manual effort in literature review through end-to-end automation

### Key Papers on Automated Literature Retrieval

1. **SciBERT** (Beltagy et al., 2019): Domain-specific BERT for scientific text
2. **CitationIE** (Nasar et al., 2018): Information extraction from citation contexts
3. **LLMs for Literature Review** (Recent work on using GPT-4/Claude for academic tasks)
4. **Semantic Scholar API** (Allen AI): Comprehensive academic search engine

## Limitations & Future Work

### Current Limitations

- **API Rate Limits**: Depends on external APIs with rate limits
- **LLM Costs**: GPT-4 analysis can be expensive for large paper sets
- **Full-Text Access**: Limited to abstracts when full text unavailable
- **Language Support**: Primarily English-language papers

### Future Enhancements

- [ ] Add support for more data sources (PubMed, Google Scholar)
- [ ] Implement full-text PDF analysis
- [ ] Add citation network analysis
- [ ] Support for non-English papers
- [ ] Fine-tuned relevance models for specific domains
- [ ] Interactive web interface

## Contributing

Contributions are welcome! Areas for improvement:

1. Additional search engines/APIs
2. Alternative relevance scoring methods
3. Better deduplication algorithms
4. Enhanced LLM prompts for analysis
5. Domain-specific configurations

## License

MIT License - see LICENSE file for details

## Acknowledgments

- SciBERT by AllenAI
- Semantic Scholar API
- arXiv API
- CrossRef API
- OpenAI and Anthropic for LLM APIs
