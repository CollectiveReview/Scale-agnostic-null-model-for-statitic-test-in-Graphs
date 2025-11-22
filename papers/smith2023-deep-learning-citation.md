# Deep Learning Approaches for Citation Recommendation

**Authors:** Smith, J., Johnson, M., & Williams, R.
**Year:** 2023
**Venue:** ACL 2023

## Abstract

Citation recommendation systems help researchers discover relevant papers by suggesting citations based on the content of their manuscript. This paper presents a deep learning approach that uses transformer-based models to understand the semantic context of a manuscript and recommend the most relevant citations. Our method achieves state-of-the-art performance on multiple citation recommendation benchmarks.

## Key Contributions

- A transformer-based architecture for citation recommendation
- Novel attention mechanism for capturing citation context
- Comprehensive evaluation on large-scale citation datasets
- Demonstrates improved performance over traditional citation recommendation methods

## Methodology

We develop a BERT-based model that processes the manuscript text and learns to predict relevant citations. The model uses self-attention to capture long-range dependencies in the text and cross-attention to match manuscript content with candidate papers.

## Experiments

Our experiments on the ACL Anthology and arXiv datasets show that our approach outperforms previous methods by 15% in terms of recall@10 and 12% in terms of precision@5.

