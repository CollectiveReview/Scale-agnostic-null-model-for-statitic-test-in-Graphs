# Graph-Based Methods for Scientific Paper Recommendation

**Authors:** Lee, H., Park, S., & Kim, J.
**Year:** 2022
**Venue:** EMNLP 2022

## Abstract

Scientific paper recommendation is crucial for researchers to discover relevant literature in their field. Traditional methods rely on citation networks and keyword matching, but recent advances in graph neural networks offer new opportunities. This paper presents a graph-based approach that leverages both citation networks and semantic relationships to recommend papers. We construct a heterogeneous graph that captures multiple types of relationships between papers, authors, and concepts, and apply graph neural networks to learn effective paper representations.

## Key Contributions

- A heterogeneous graph construction method for scientific literature
- Graph neural network architecture for paper recommendation
- Evaluation on real-world citation datasets showing 20% improvement over baselines
- Analysis of different graph structures and their impact on recommendation quality

## Methodology

We construct a heterogeneous graph where nodes represent papers, authors, and concepts, and edges represent citations, authorship, and semantic relationships. A graph neural network with attention mechanisms learns node embeddings that capture the complex relationships in the graph.

## Results

Our experiments on the ACL Anthology and DBLP datasets demonstrate significant improvements in recommendation accuracy, particularly for emerging research topics with sparse citation networks.

