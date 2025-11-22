#!/bin/bash
# Example usage script for the literature retrieval system

echo "======================================"
echo "Literature Retrieval System - Examples"
echo "======================================"
echo ""

# Example 1: Basic search
echo "Example 1: Basic search for citation context analysis"
echo "Command: python main.py 'citation context analysis' --no-pr"
echo ""

# Example 2: Search with context
echo "Example 2: Search with research context"
echo "Command: python main.py 'graph neural networks' --context 'Application to citation networks and bibliometric analysis' --no-pr"
echo ""

# Example 3: Create PR (requires GitHub token)
echo "Example 3: Search and create PR"
echo "Command: export GITHUB_TOKEN='your-token' && python main.py 'scale-agnostic null models for network analysis'"
echo ""

# Example 4: Custom config
echo "Example 4: Use custom configuration"
echo "Command: python main.py 'your query' --config custom_config.yaml"
echo ""

echo "======================================"
echo "To run an example, copy and paste the command after 'Command:'"
echo "======================================"
