# Adobe Hackathon 2025 - Problem 1(a) Solution

## PDF Structure Extraction

This solution addresses **Problem 1(a)** of the Adobe Hackathon 2025 "Connecting the Dots Challenge" - extracting structured outlines from PDF documents including document titles and hierarchical headings.

## Features

### Enhanced PDF Outline Extraction

- **Multi-strategy title detection**: Metadata, font analysis, positioning, and filename fallbacks
- **Advanced heading hierarchy detection**: Font size analysis with intelligent level mapping
- **Robust heading identification**: Uses multiple criteria including:
  - Font size and styling (bold, italic)
  - Text patterns and keywords
  - Numbering schemes (1., 1.1, Chapter 1, etc.)
  - Position and context analysis
- **Data cleaning and validation**: Removes duplicates, normalizes text, filters noise

### Output Format

The solution generates JSON files with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter 1: Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "1.1 Background",
      "page": 2
    }
  ]
}
```

## Requirements

- Python 3.7+
- PyMuPDF (fitz) library for PDF processing

## Installation

1. **Install Python dependencies:**

```bash
pip install PyMuPDF
```

2. **Download the solution files:**
   - `solution_1a.py` - Main solution
   - `test_solution_1a.py` - Testing and validation script
   - `README.md` - This documentation

## Usage

### Process Single PDF

```bash
python solution_1a.py path/to/document.pdf
```

### Process Dataset Directory

```bash
python solution_1a.py input_directory output_directory
```

### Test Against Dataset

```bash
python test_solution_1a.py Datasets
```

### Test with Output Generation

```bash
python test_solution_1a.py Datasets test_output
```

## Examples

### Example 1: Processing the provided dataset

```bash
# Process all PDFs in the Datasets/Pdfs directory
python solution_1a.py Datasets/Pdfs Results

# Test against expected outputs
python test_solution_1a.py Datasets Results
```

### Example 2: Single PDF analysis

```bash
# Analyze a specific PDF file
python solution_1a.py Datasets/Pdfs/STEMPathwaysFlyer.pdf
```

Expected output:

```json
{
  "title": "",
  "outline": [
    {
      "level": "H1",
      "text": "Parsippany -Troy Hills STEM Pathways",
      "page": 1
    },
    {
      "level": "H2",
      "text": "PATHWAY OPTIONS",
      "page": 1
    }
  ]
}
```

## Algorithm Overview

### 1. Title Extraction Strategy

1. **Metadata Analysis**: Check PDF metadata for title field
2. **Font Analysis**: Identify largest fonts in document header
3. **Position Analysis**: Look for title-like text at top of first page
4. **Style Analysis**: Consider bold/emphasized text
5. **Filename Fallback**: Use filename if no title found

### 2. Heading Detection Pipeline

1. **Text Extraction**: Extract all text with font and position information
2. **Font Analysis**: Determine body text size and heading font sizes
3. **Hierarchy Mapping**: Map font sizes to heading levels (H1-H4)
4. **Pattern Recognition**: Identify headings using multiple criteria:
   - Font size relative to body text
   - Bold/italic styling
   - Numbering patterns
   - Keyword analysis
   - Text length and ending patterns
5. **Validation & Cleaning**: Remove duplicates, normalize text, filter noise

### 3. Scoring System

The heading detection uses a weighted scoring system:

- **Bold text**: +2 points
- **Larger font**: +2 points
- **Proper ending** (no period): +1 point
- **Heading keywords**: +2 points
- **Numbering pattern**: +3 points

Minimum score of 3 required for heading classification.

## Performance Metrics

The test script provides comprehensive metrics:

- **Precision**: Correctly identified headings / Total identified headings
- **Recall**: Correctly identified headings / Total expected headings
- **F1 Score**: Harmonic mean of precision and recall
- **Title Match**: Exact title matching accuracy
- **Overall Score**: Combined title and outline performance

## Dataset Analysis

Based on the provided dataset, the solution handles various document types:

| Document          | Type        | Complexity | Headings             |
| ----------------- | ----------- | ---------- | -------------------- |
| E0CCG5S239        | Form        | Simple     | Title only           |
| E0CCG5S312        | Technical   | Medium     | H1, H2 (18 headings) |
| E0H1CM114         | Business    | Complex    | H1-H4 (37 headings)  |
| STEMPathwaysFlyer | Educational | Medium     | H1-H3 (4 headings)   |
| TOPJUMP           | Invitation  | Simple     | H1 (1 heading)       |

## Limitations and Considerations

1. **Font-based Detection**: Relies on consistent font sizing for hierarchy
2. **Language Support**: Optimized for English documents
3. **Complex Layouts**: May struggle with multi-column or artistic layouts
4. **Image-based Text**: Cannot extract text from images or scanned PDFs
5. **Model Size**: Designed to meet the 200MB constraint for Round 1A

## Technical Implementation

### Key Classes

- `EnhancedPDFOutlineExtractor`: Main extraction engine
- Font analysis and hierarchy detection methods
- Text cleaning and validation utilities

### Dependencies

- **PyMuPDF (fitz)**: PDF processing and text extraction
- **Python Standard Library**: json, pathlib, re, collections

### Performance Optimizations

- Single-pass text extraction with caching
- Efficient font size analysis using Counter
- Optimized regex patterns for text classification
- Memory-conscious processing for large documents

## Contributing

This solution is designed for the Adobe Hackathon 2025. For improvements or bug reports related to the challenge, please ensure any modifications maintain compatibility with the expected output format and constraints.

## License

Created for Adobe Hackathon 2025 - Connecting the Dots Challenge.
