# Synthetic Dataset Generator Guide

## Overview

The synthetic dataset generator creates realistic PDF documents with known structures for testing and improving the PDF outline extraction solution. It generates 8 different types of documents with varying complexity levels.

## Quick Start

### Generate 25 Documents (Default)

```bash
python generate_synthetic_dataset.py --num-docs 25
```

### Generate and Test Immediately

```bash
python generate_synthetic_dataset.py --num-docs 25 --test
```

### Custom Output Directory

```bash
python generate_synthetic_dataset.py --num-docs 50 --output-dir CustomDataset
```

## Document Types Generated

The generator creates 8 different document templates:

### 1. **Technical Reports**

- **Structure**: Executive Summary → Introduction → Technical Architecture → Results → Conclusion
- **Complexity**: Medium (16 headings)
- **Levels**: H1, H2, H3
- **Example**: "System Architecture Design for Machine Learning"

### 2. **Business Proposals**

- **Structure**: Executive Summary → Company Overview → Market Analysis → Proposed Solution → Investment
- **Complexity**: Medium-High (19 headings)
- **Levels**: H1, H2, H3
- **Example**: "Strategic Business Plan for TechCorp"

### 3. **Academic Papers**

- **Structure**: Abstract → Introduction → Literature Review → Methodology → Results → Discussion → Conclusion
- **Complexity**: High (24 headings)
- **Levels**: H1, H2, H3
- **Example**: "Research Study on Neural Networks in Computer Science"

### 4. **User Manuals**

- **Structure**: Getting Started → Installation → Basic Operations → Features → Troubleshooting → Support
- **Complexity**: Medium-High (22 headings)
- **Levels**: H1, H2, H3
- **Example**: "User Manual: Software Application v2.1"

### 5. **Policy Documents**

- **Structure**: Policy Overview → Definitions → Policy Statement → Implementation → Compliance → Enforcement
- **Complexity**: High (22 headings)
- **Levels**: H1, H2, H3
- **Example**: "Data Privacy Policy Document"

### 6. **Research Papers**

- **Structure**: Abstract → Introduction → Background → Methodology → Analysis → Findings → Future Research
- **Complexity**: High (23 headings)
- **Levels**: H1, H2, H3
- **Example**: "Research on Artificial Intelligence: Current Trends and Future Directions"

### 7. **Project Plans**

- **Structure**: Project Overview → Scope → Team → Timeline → Risk Management → Budget → QA
- **Complexity**: Very High (27 headings)
- **Levels**: H1, H2, H3
- **Example**: "Project Plan: Software Development Implementation"

### 8. **Training Manuals**

- **Structure**: Introduction → Module 1 → Module 2 → Module 3 → Assessment → Certification → Resources
- **Complexity**: Very High (27 headings)
- **Levels**: H1, H2, H3
- **Example**: "Training Manual: Technical Skills Certification Program"

## Output Structure

### Directory Layout

```
SyntheticDataset/
├── Pdfs/                    # Generated PDF files
│   ├── SYNTH_001.pdf
│   ├── SYNTH_002.pdf
│   └── ...
├── Output.json/             # Expected JSON outputs
│   ├── SYNTH_001.json
│   ├── SYNTH_002.json
│   └── ...
└── dataset_metadata.json   # Dataset statistics
```

### Sample JSON Output

```json
{
  "title": "Security Policy Document",
  "outline": [
    {
      "level": "H1",
      "text": "Policy Overview",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Purpose",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Scope",
      "page": 1
    }
  ]
}
```

## Advanced Usage

### Testing Specific Document Types

```python
from generate_synthetic_dataset import SyntheticPDFGenerator

generator = SyntheticPDFGenerator()

# Generate only technical reports
title, structure = generator.generate_technical_report("TEST_001")
print(f"Title: {title}")
print(f"Headings: {len(structure['outline'])}")
```

### Analyzing Dataset Statistics

```bash
# Generate dataset with metadata
python generate_synthetic_dataset.py --num-docs 100

# View statistics
cat SyntheticDataset/dataset_metadata.json
```

## Performance Analysis

### Complexity Distribution

Based on our testing with 25 documents:

| Document Type      | Avg Headings | Complexity  | Success Rate |
| ------------------ | ------------ | ----------- | ------------ |
| Technical Reports  | 16           | Medium      | 91%          |
| Business Proposals | 19           | Medium-High | 91%          |
| Academic Papers    | 24           | High        | 89%          |
| User Manuals       | 22           | Medium-High | 86%          |
| Policy Documents   | 22           | High        | 93%          |
| Research Papers    | 23           | High        | 40%\*        |
| Project Plans      | 27           | Very High   | 89%          |
| Training Manuals   | 27           | Very High   | 42%\*        |

\* Lower scores due to title truncation issues with long titles

### Overall Performance Metrics

- **Average Title Match**: 68%
- **Average Outline F1 Score**: 83%
- **Average Overall Score**: 75%

## Customization Options

### Adding New Document Types

```python
def generate_custom_document(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
    """Generate a custom document structure."""
    title = "Custom Document Title"

    structure = [
        ("H1", "Custom Section 1"),
        ("H2", "Custom Subsection 1.1"),
        ("H2", "Custom Subsection 1.2"),
        ("H1", "Custom Section 2"),
    ]

    return title, self.create_outline_structure(structure)

# Add to document_templates list
self.document_templates.append(self.generate_custom_document)
```

### Modifying Content Generation

```python
# Customize heading pools in __init__
self.heading_pools['H1'].extend([
    "Custom Heading 1",
    "Custom Heading 2"
])

# Customize title templates
self.title_templates['custom'] = [
    "Custom Title Template: {variable}"
]
```

## Testing and Validation

### Run Complete Test Suite

```bash
# Generate dataset and test solution
python generate_synthetic_dataset.py --num-docs 50 --test

# Or test existing dataset
python test_solution_1a.py SyntheticDataset SyntheticResults
```

### Performance Benchmarking

```bash
# Generate larger dataset for benchmarking
python generate_synthetic_dataset.py --num-docs 100 --output-dir BenchmarkDataset

# Test performance
time python test_solution_1a.py BenchmarkDataset BenchmarkResults
```

## Tips for Best Results

### Document Generation

1. **Vary Document Count**: Test with different sizes (10, 25, 50, 100 documents)
2. **Multiple Runs**: Generate several datasets to test consistency
3. **Custom Templates**: Add domain-specific document types for targeted testing

### Testing Strategy

1. **Baseline Testing**: Start with 25 documents to establish baseline performance
2. **Scaling Tests**: Increase to 100+ documents for comprehensive evaluation
3. **Edge Case Testing**: Create documents with unusual structures

### Performance Optimization

1. **Pattern Analysis**: Identify which document types perform best/worst
2. **Iterative Improvement**: Use results to refine the solution
3. **A/B Testing**: Compare different parameter settings

## Integration with Main Solution

### Automated Testing Pipeline

```bash
#!/bin/bash
# automated_test.sh

echo "Generating synthetic dataset..."
python generate_synthetic_dataset.py --num-docs 25

echo "Testing original dataset..."
python test_solution_1a.py Datasets OriginalResults

echo "Testing synthetic dataset..."
python test_solution_1a.py SyntheticDataset SyntheticResults

echo "Comparing results..."
# Add result comparison logic here
```

### Continuous Improvement

1. **Regular Generation**: Create new datasets weekly
2. **Performance Tracking**: Monitor scores over time
3. **Solution Refinement**: Use insights to improve extraction algorithms

## Dependencies

- **reportlab**: PDF generation
- **PyMuPDF**: PDF processing (for testing)
- **Python 3.7+**: Core functionality

## Contributing

To add new document types or improve existing ones:

1. **Create New Template**: Add method to `SyntheticPDFGenerator`
2. **Define Structure**: Specify heading hierarchy and content
3. **Add to Templates**: Include in `document_templates` list
4. **Test Generation**: Verify PDF and JSON output
5. **Update Documentation**: Add to this guide

## Troubleshooting

### Common Issues

**Issue**: PDF generation fails
**Solution**: Ensure reportlab is installed: `pip install reportlab`

**Issue**: Low performance scores
**Solution**: Check if solution_1a.py is in the same directory

**Issue**: Memory issues with large datasets
**Solution**: Generate in smaller batches (e.g., 25 documents at a time)

**Issue**: Inconsistent results
**Solution**: Set random seed for reproducible generation

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Generate single document for debugging
generator = SyntheticPDFGenerator()
result = generator.generate_document("DEBUG_001", "DebugOutput")
```

This synthetic dataset generator provides a robust foundation for testing and improving PDF outline extraction solutions, offering realistic document structures across various domains and complexity levels.
