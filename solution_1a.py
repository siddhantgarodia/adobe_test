#!/usr/bin/env python3
"""
Adobe Hackathon 2025 - Problem 1(a): PDF Structure Extraction
Enhanced solution for extracting structured outlines from PDF documents

Author: Assistant
Date: 2025
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import logging
import re
from collections import Counter, defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPDFOutlineExtractor:
    """
    Enhanced PDF outline extractor for Problem 1(a).
    Improved title detection and hierarchical heading extraction.
    """
    
    def __init__(self):
        self.min_title_font_ratio = 1.2  # Title should be at least 20% larger than body text
        self.heading_keywords = {
            'H1': ['chapter', 'section', 'part', 'introduction', 'background', 'overview', 'summary', 'conclusion'],
            'H2': ['subsection', 'method', 'approach', 'requirements', 'implementation', 'results'],
            'H3': ['procedure', 'step', 'phase', 'component', 'feature']
        }
        
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured outline from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with title and outline structure
        """
        try:
            import fitz  # PyMuPDF for PDF processing
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return {"title": "", "outline": []}
            
            doc = fitz.open(pdf_path)
            
            # Extract title from document
            title = self._extract_title(doc)
            
            # Extract headings with improved hierarchy detection
            outline = self._extract_headings_enhanced(doc)
            
            doc.close()
            
            result = {
                "title": title.strip(),
                "outline": outline
            }
            
            logger.info(f"Successfully extracted outline from {os.path.basename(pdf_path)}")
            logger.info(f"Title: '{title}'")
            logger.info(f"Found {len(outline)} headings")
            
            return result
            
        except ImportError:
            logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
            return {"title": "", "outline": []}
        except Exception as e:
            logger.error(f"Error extracting outline from {pdf_path}: {str(e)}")
            return {"title": "", "outline": []}
    
    def _extract_title(self, doc) -> str:
        """Enhanced title extraction with multiple strategies."""
        
        # Strategy 1: Analyze first page for title-like text (prioritized over metadata)
        if len(doc) > 0:
            first_page = doc[0]
            
            # Get text with font information
            blocks = first_page.get_text("dict")["blocks"]
            
            # Collect text elements with their properties
            text_elements = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 3:  # Ignore very short text
                                text_elements.append({
                                    "text": text,
                                    "size": span["size"],
                                    "flags": span["flags"],  # Font style flags
                                    "bbox": span["bbox"],
                                    "y": span["bbox"][1]  # Y coordinate for position
                                })
            
            if text_elements:
                # Sort by Y position (top to bottom)
                text_elements.sort(key=lambda x: x["y"])
                
                # Strategy 1a: Look for largest font in top portion
                top_elements = [elem for elem in text_elements if elem["y"] < 300]  # Increased search area
                if top_elements:
                    max_size = max(elem["size"] for elem in top_elements)
                    title_candidates = [elem for elem in top_elements if elem["size"] >= max_size * 0.85]
                    
                    # Prefer elements that look like titles
                    for candidate in title_candidates:
                        text = candidate["text"]
                        # Skip obvious non-titles
                        if (text.lower().startswith(('page ', 'figure ', 'table ')) or
                            text.isdigit() or
                            len(text) < 5 or
                            text.lower().endswith(('.doc', '.pdf', '.cdr')) or
                            'microsoft word' in text.lower()):
                            continue
                        # Good title candidate
                        if len(text) > 5 and len(text) < 200:
                            return text
                
                # Strategy 1b: Look for centered text at top
                for elem in text_elements[:15]:  # Check first 15 elements
                    text = elem["text"]
                    bbox = elem["bbox"]
                    # Check if text is somewhat centered (simple heuristic)
                    if (bbox[0] > 50 and  # Not at far left
                        len(text) > 10 and len(text) < 200 and
                        not text.lower().startswith(('page ', 'figure ', 'table ')) and
                        not text.isdigit() and
                        not text.lower().endswith(('.doc', '.pdf', '.cdr')) and
                        'microsoft word' not in text.lower()):
                        return text
        
        # Strategy 2: Document metadata (as fallback)
        metadata = doc.metadata
        if metadata and metadata.get('title') and len(metadata['title'].strip()) > 0:
            title = metadata['title'].strip()
            # Skip technical filenames
            if (not title.lower().endswith(('.pdf', '.doc', '.cdr')) and
                'microsoft word' not in title.lower() and
                len(title) > 5):
                return title
        
        # Strategy 3: Return empty string (many documents don't have clear titles)
        return ""
    
    def _extract_headings_enhanced(self, doc) -> List[Dict[str, Any]]:
        """Enhanced heading extraction with better hierarchy detection."""
        
        all_text_elements = []
        font_sizes = []
        
        # First pass: collect all text elements with their properties
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            page_elements = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_size = 0
                        line_flags = 0
                        line_bbox = None
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            line_size = max(line_size, span["size"])
                            line_flags |= span["flags"]
                            if line_bbox is None:
                                line_bbox = span["bbox"]
                        
                        line_text = line_text.strip()
                        if line_text and len(line_text) > 1:
                            element = {
                                "text": line_text,
                                "size": line_size,
                                "flags": line_flags,
                                "bbox": line_bbox,
                                "page": page_num,
                                "y": line_bbox[1] if line_bbox else 0
                            }
                            page_elements.append(element)
                            font_sizes.append(line_size)
            
            all_text_elements.extend(page_elements)
        
        if not all_text_elements:
            return []
        
        # Analyze font sizes to determine hierarchy
        font_counter = Counter(font_sizes)
        sorted_sizes = sorted(font_counter.keys(), reverse=True)
        
        # Determine body text size (most common size)
        body_size = font_counter.most_common(1)[0][0]
        
        # Create size-to-level mapping
        size_to_level = self._create_heading_levels(sorted_sizes, body_size)
        
        # Second pass: identify headings
        headings = []
        for element in all_text_elements:
            if self._is_heading(element, size_to_level, body_size):
                level = size_to_level.get(element["size"], None)
                if level:
                    heading = {
                        "level": level,
                        "text": element["text"],
                        "page": element["page"] + 1  # Convert to 1-indexed
                    }
                    headings.append(heading)
        
        # Clean and validate headings
        cleaned_headings = self._clean_headings(headings)
        
        return cleaned_headings
    
    def _create_heading_levels(self, sorted_sizes: List[float], body_size: float) -> Dict[float, str]:
        """Create mapping from font size to heading level."""
        size_to_level = {}
        level_names = ["H1", "H2", "H3", "H4"]
        level_idx = 0
        
        # More conservative approach - only use clearly larger fonts
        for size in sorted_sizes:
            # Only consider sizes significantly larger than body text for headings
            if size > body_size * 1.2 and level_idx < len(level_names):
                size_to_level[size] = level_names[level_idx]
                level_idx += 1
        
        return size_to_level
    
    def _is_heading(self, element: Dict[str, Any], size_to_level: Dict[float, str], body_size: float) -> bool:
        """Determine if a text element is likely a heading."""
        text = element["text"]
        size = element["size"]
        flags = element["flags"]
        
        # Basic criteria
        if size not in size_to_level:
            return False
        
        # Length criteria - be more restrictive
        if len(text) < 3 or len(text) > 150:
            return False
        
        # Exclude page numbers and common non-heading patterns
        if (text.isdigit() or 
            text.startswith(('Page ', 'Figure ', 'Table ', 'www.', 'http', 'RSVP')) or
            re.match(r'^\d+(\.\d+)*$', text) or  # Just numbers with dots
            re.match(r'^-+$', text) or  # Just dashes
            text.endswith('...') or
            text.count('-') > 5 or  # Lines with many dashes
            text.lower().startswith(('march ', 'january ', 'february ')) or  # Dates
            text.lower().endswith(('.com', '.org', '.pdf', '.doc'))):
            return False
        
        # Additional filtering for common non-headings
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in [
            'microsoft word', 'to provide', 'students with', 'opportunity to'
        ]):
            return False
        
        # Positive indicators
        is_bold = bool(flags & 2**4)  # Bold flag
        is_larger = size > body_size * 1.2  # More conservative
        ends_properly = not text.endswith('.')  # Headings usually don't end with periods
        
        # Keyword-based boost
        has_heading_keywords = any(
            keyword in text_lower 
            for keywords in self.heading_keywords.values() 
            for keyword in keywords
        )
        
        # Numbering patterns (like "1.", "1.1", "Chapter 1", etc.)
        has_numbering = bool(re.match(r'^(\d+\.|\d+\.\d+|Chapter \d+|Section \d+|Appendix [A-Z])', text, re.IGNORECASE))
        
        # Title case or ALL CAPS (common for headings)
        is_title_case = text.istitle() or text.isupper()
        
        # Make decision with higher threshold
        score = 0
        if is_bold: score += 3
        if is_larger: score += 3
        if ends_properly: score += 1
        if has_heading_keywords: score += 2
        if has_numbering: score += 4
        if is_title_case: score += 1
        
        return score >= 4  # Higher threshold
    
    def _clean_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate the extracted headings."""
        cleaned = []
        seen_texts = set()
        
        for heading in headings:
            text = heading["text"].strip()
            
            # Remove duplicates
            if text.lower() in seen_texts:
                continue
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            
            if len(text) >= 3:  # Minimum length check
                heading["text"] = text
                cleaned.append(heading)
                seen_texts.add(text.lower())
        
        return cleaned


def process_dataset(input_dir: str, output_dir: str) -> None:
    """Process all PDFs in the dataset directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    extractor = EnhancedPDFOutlineExtractor()
    
    # Process all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Processing {len(pdf_files)} PDF files...")
    
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file.name}...")
        
        try:
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Save result
            output_file = output_path / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Saved result to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")


def test_single_pdf(pdf_path: str) -> None:
    """Test the extractor on a single PDF file."""
    extractor = EnhancedPDFOutlineExtractor()
    result = extractor.extract_outline(pdf_path)
    
    print("\n" + "="*50)
    print(f"Results for: {os.path.basename(pdf_path)}")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python solution_1a.py <pdf_file>           # Test single PDF")
        print("  python solution_1a.py <input_dir> <output_dir>  # Process dataset")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Single PDF mode
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found: {pdf_path}")
            sys.exit(1)
        test_single_pdf(pdf_path)
    
    elif len(sys.argv) == 3:
        # Dataset processing mode
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        
        if not os.path.exists(input_dir):
            print(f"Error: Input directory not found: {input_dir}")
            sys.exit(1)
            
        process_dataset(input_dir, output_dir)
    
    else:
        print("Error: Too many arguments")
        sys.exit(1)


if __name__ == "__main__":
    main() 