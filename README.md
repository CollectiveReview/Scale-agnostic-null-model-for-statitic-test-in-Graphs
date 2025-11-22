# Scale-agnostic Null Model for Statistical Tests in Graphs

Research repository for citation context analysis and scale-agnostic null models for network statistics.

## Overview

This repository contains research materials and tools for analyzing citation contexts and developing scale-agnostic null models for statistical testing in graph networks.

## Automated Literature Retrieval System

We provide an automated pipeline for discovering, analyzing, and suggesting relevant academic literature. The system uses:

- **Multi-source search** across Semantic Scholar, arXiv, and CrossRef
- **SciBERT embeddings** for semantic relevance scoring
- **LLM analysis** (GPT-4/Claude) for paper assessment
- **Automated GitHub PR creation** for literature suggestions

### Quick Start

```bash
cd literature_retrieval
pip install -r requirements.txt

# Set up API keys (optional but recommended)
export OPENAI_API_KEY="your-key"
export GITHUB_TOKEN="your-token"

# Run literature search
python main.py "your research topic"
```

For detailed documentation, see [literature_retrieval/README.md](literature_retrieval/README.md)

## Contributing

Contributions are welcome! Please see the individual module documentation for details.

## License

MIT License - see LICENSE file for details
