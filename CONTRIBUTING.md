# Contributing to Citation Context Literature Review

Thank you for contributing to this literature review repository! This guide will help you add papers and related research to the collection.

## Adding a New Paper

1. **Create a new markdown file** in the `papers/` directory with a descriptive filename:
   ```bash
   papers/author-year-topic.md
   ```

2. **Use the following template**:

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
   
   ## Methodology
   
   (Optional) Description of methods...
   
   ## Experiments
   
   (Optional) Description of experiments and results...
   ```

3. **Commit and push** your changes:
   ```bash
   git add papers/your-paper.md
   git commit -m "Add paper: Title of the paper"
   git push
   ```

4. **Wait for the bot**: The GitHub Actions bot will automatically:
   - Analyze your paper's content
   - Match it with related research from the `related_research/` directory
   - Create a pull request with suggested related work

5. **Review the PR**: Check the bot's suggestions and merge if they look good!

## Adding Related Research

To expand the bot's knowledge base:

1. **Create a new markdown file** in the `related_research/` directory:
   ```bash
   related_research/author-year-topic.md
   ```

2. **Use the following template**:

   ```markdown
   # Research Title
   
   **Keywords:** keyword1, keyword2, keyword3, citation, analysis
   **Year:** Publication year
   **Authors:** Author names
   
   ## Summary
   
   Brief summary of the research (2-3 sentences)...
   
   ## Key Contributions
   
   - Main contribution 1
   - Main contribution 2
   
   ## Relevance
   
   Why this research is relevant for citation context analysis...
   ```

3. **Important**: Include relevant keywords that will help the bot match this research with appropriate papers!

## Testing Locally

Before committing, you can test the bot locally:

```bash
python scripts/suggest_related_research.py papers/your-paper.md
```

This will show you what related research would be suggested for your paper.

## Workflow Triggers

The bot automatically runs when:
- A paper is added or modified in the `papers/` directory on the `main` branch
- A pull request contains changes to files in `papers/`

## Tips for Better Matching

To improve the bot's suggestions:

1. **Use specific keywords**: Include domain-specific terms in your paper content
2. **Write detailed abstracts**: More content gives the bot better context
3. **Add keywords to related research**: Make sure related research files have comprehensive keyword lists
4. **Review and edit**: The bot's suggestions are starting points - feel free to edit them!

## Questions or Issues?

If you encounter any problems or have suggestions for improving the bot, please open an issue in the repository.
