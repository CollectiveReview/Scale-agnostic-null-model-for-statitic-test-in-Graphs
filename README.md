# citation_context

Literature review of citation context analysis with automated research suggestion bot.

## Overview

This repository provides an automated system for managing a literature review on citation context analysis. When new papers are added to the `papers/` directory, a GitHub Actions bot automatically analyzes the content and suggests related research.

## Features

- 🤖 **Automated Research Suggestions**: GitHub Actions bot automatically identifies and suggests related research
- 📚 **Structured Paper Repository**: Organized directory structure for papers and related research
- 🔍 **Keyword-Based Matching**: Intelligent keyword extraction and matching algorithm
- 🔄 **Automatic PR Creation**: Bot creates pull requests with suggested citations

## How It Works

1. **Add a Paper**: Create a new markdown file in the `papers/` directory following the template
2. **Automatic Analysis**: When you push to the main branch, the GitHub Actions workflow triggers
3. **Related Research**: The bot analyzes the paper content and matches it with research in `related_research/`
4. **Pull Request**: An automatic PR is created with the related research suggestions
5. **Review & Merge**: Review the suggestions and merge the PR

## Directory Structure

```
.
├── papers/              # Research papers for review
├── related_research/    # Database of related research
├── scripts/            # Bot scripts
│   └── suggest_related_research.py
└── .github/
    └── workflows/      # GitHub Actions workflows
        └── suggest-related-research.yml
```

## Adding a New Paper

Create a new markdown file in the `papers/` directory with the following format:

```markdown
# Paper Title

**Authors:** Author names
**Year:** Publication year
**Venue:** Conference/Journal name

## Abstract

Paper abstract here...

## Key Contributions

- Main contribution 1
- Main contribution 2
```

The bot will automatically add a "Related Work" section when you push the file.

## Adding Related Research

To expand the bot's knowledge base, add new research to the `related_research/` directory:

```markdown
# Research Title

**Keywords:** keyword1, keyword2, keyword3
**Year:** Publication year
**Authors:** Author names

## Summary

Brief summary...

## Relevance

Why this research is relevant...
```

## Manual Testing

You can manually test the bot locally:

```bash
python scripts/suggest_related_research.py papers/your-paper.md
```

## Requirements

- Python 3.11+
- GitHub Actions (automatically configured)
