# Related Research

This directory contains automatically generated literature reviews on topics related to scale-agnostic null models and citation context analysis.

## How Literature is Added

Literature files in this directory are automatically generated using the `/literature_retrieval` automation system, which:

1. Searches multiple academic databases (Semantic Scholar, arXiv, CrossRef)
2. Scores papers for relevance using SciBERT embeddings
3. Analyzes top papers using LLM (GPT-4/Claude)
4. Creates pull requests with formatted literature suggestions

## Manual Review

All automatically suggested literature should be reviewed before merging to ensure:
- Relevance to the research topic
- Quality and reliability of sources
- Proper citation formatting
- No duplicate papers

## Adding New Topics

To suggest literature for a new topic:

```bash
cd literature_retrieval
python main.py "your research topic" --context "Additional context for relevance"
```

This will create a pull request with the suggested papers for review.
