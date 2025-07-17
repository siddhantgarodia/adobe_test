#!/usr/bin/env python3
"""
Adobe Hackathon 2025 - Problem 1(a): Context-Aware PDF Structure Extraction
Enhanced solution for extracting structured outlines using context instead of font differences

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
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextAwarePDFExtractor:
    """
    Context-aware PDF outline extractor for uniform font documents.
    Uses positioning, indentation, patterns, and semantic analysis.
    """
    
    def __init__(self):
        # Semantic patterns for heading identification
        self.heading_indicators = {
            'chapter_patterns': [
                r'^chapter\s+\d+', r'^part\s+[ivxlc]+', r'^section\s+\d+',
                r'^article\s+[ivxlc]+', r'^title\s+[ivxlc]+', r'^book\s+[ivxlc]+'
            ],
            'numbering_patterns': [
                r'^\d+\.$',  # "1."
                r'^\d+\.\d+$',  # "1.1"  
                r'^\d+\.\d+\.\d+$',  # "1.1.1"
                r'^\d+\.\d+\.\d+\.\d+$',  # "1.1.1.1"
                r'^[IVXLC]+\.$',  # "I.", "II.", etc.
                r'^[A-Z]\.$',  # "A.", "B.", etc.
                r'^[a-z]\.$',  # "a.", "b.", etc.
                r'^\([a-z]\)$',  # "(a)", "(b)", etc.
                r'^\(\d+\)$'  # "(1)", "(2)", etc.
            ],
            'semantic_markers': [
                'introduction', 'background', 'methodology', 'methods', 'results', 
                'discussion', 'conclusion', 'summary', 'abstract', 'overview',
                'objectives', 'scope', 'requirements', 'implementation', 'analysis',
                'recommendations', 'appendix', 'references', 'bibliography',
                'acknowledgments', 'preface', 'executive summary', 'table of contents'
            ],
            'structural_words': [
                'section', 'chapter', 'part', 'article', 'clause', 'subsection',
                'paragraph', 'subparagraph', 'item', 'subitem', 'point', 'subpoint'
            ]
        }
        
        # Indentation thresholds for hierarchy detection
        self.indentation_levels = {
            'H1': (0, 0.5),      # 0 to 0.5 inch indentation
            'H2': (0.25, 1.0),   # 0.25 to 1.0 inch indentation  
            'H3': (0.5, 1.5),    # 0.5 to 1.5 inch indentation
            'H4': (0.75, 2.0)    # 0.75 to 2.0 inch indentation
        }
        
        # Y-position thresholds for title detection
        self.title_region = (50, 200)  # Top 200 points of first page
        
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Extract structured outline using context-aware analysis."""
        try:
            import fitz  # PyMuPDF for PDF processing
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return {"title": "", "outline": []}
            
            doc = fitz.open(pdf_path)
            
            # Extract title using context analysis
            title = self._extract_title_context_aware(doc)
            
            # Extract text elements with full context
            text_elements = self._extract_text_with_context(doc)
            
            # Identify headings using context analysis
            headings = self._identify_headings_by_context(text_elements)
            
            # Assign hierarchy levels based on context
            outline = self._assign_hierarchy_levels(headings)
            
            doc.close()
            
            result = {
                "title": title.strip(),
                "outline": outline
            }
            
            logger.info(f"Context-aware extraction from {os.path.basename(pdf_path)}")
            logger.info(f"Title: '{title}'")
            logger.info(f"Found {len(outline)} headings using context analysis")
            
            return result
            
        except ImportError:
            logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
            return {"title": "", "outline": []}
        except Exception as e:
            logger.error(f"Error extracting outline from {pdf_path}: {str(e)}")
            return {"title": "", "outline": []}
    
    def _extract_title_context_aware(self, doc) -> str:
        """Extract title using position, centering, and context analysis."""
        if len(doc) == 0:
            return ""
        
        first_page = doc[0]
        page_width = first_page.rect.width
        
        # Get all text blocks from first page
        blocks = first_page.get_text("dict")["blocks"]
        
        title_candidates = []
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        bbox = span["bbox"]
                        
                        # Skip obvious non-titles
                        if (len(text) < 5 or len(text) > 200 or
                            text.isdigit() or
                            text.lower().startswith(('page ', 'figure ', 'table ')) or
                            text.lower().endswith(('.pdf', '.doc', '.docx')) or
                            'microsoft word' in text.lower()):
                            continue
                        
                        # Analyze position context
                        y_pos = bbox[1]
                        x_pos = bbox[0]
                        text_width = bbox[2] - bbox[0]
                        
                        # Check if in title region (top of page)
                        if y_pos <= self.title_region[1]:
                            # Calculate centering score
                            page_center = page_width / 2
                            text_center = x_pos + (text_width / 2)
                            centering_score = 1 - abs(text_center - page_center) / page_center
                            
                            # Position score (higher for top of page)
                            position_score = 1 - (y_pos / self.title_region[1])
                            
                            # Length score (prefer reasonable title lengths)
                            length_score = 1 - abs(len(text) - 50) / 100  # Optimal around 50 chars
                            length_score = max(0, length_score)
                            
                            # Capitalization score
                            cap_score = 0.5
                            if text.isupper():
                                cap_score = 1.0
                            elif text.istitle():
                                cap_score = 0.8
                            
                            # Composite score
                            total_score = (
                                centering_score * 0.3 +
                                position_score * 0.3 +
                                length_score * 0.2 +
                                cap_score * 0.2
                            )
                            
                            title_candidates.append({
                                'text': text,
                                'score': total_score,
                                'y_pos': y_pos
                            })
        
        if title_candidates:
            # Sort by score and return best candidate
            title_candidates.sort(key=lambda x: x['score'], reverse=True)
            return title_candidates[0]['text']
        
        return ""
    
    def _extract_text_with_context(self, doc) -> List[Dict[str, Any]]:
        """Extract all text elements with comprehensive context information."""
        text_elements = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_width = page.rect.width
            page_height = page.rect.height
            
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        # Combine spans in the same line
                        line_text = ""
                        line_bbox = None
                        line_flags = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            line_flags |= span["flags"]
                            if line_bbox is None:
                                line_bbox = span["bbox"]
                            else:
                                # Expand bbox to include this span
                                line_bbox = (
                                    min(line_bbox[0], span["bbox"][0]),
                                    min(line_bbox[1], span["bbox"][1]),
                                    max(line_bbox[2], span["bbox"][2]),
                                    max(line_bbox[3], span["bbox"][3])
                                )
                        
                        line_text = line_text.strip()
                        if not line_text or len(line_text) < 2:
                            continue
                        
                        # Calculate context features
                        x_pos = line_bbox[0]
                        y_pos = line_bbox[1]
                        text_width = line_bbox[2] - line_bbox[0]
                        text_height = line_bbox[3] - line_bbox[1]
                        
                        # Indentation level (normalized)
                        indentation = x_pos / 72  # Convert to inches
                        
                        # Centering score
                        page_center = page_width / 2
                        text_center = x_pos + (text_width / 2)
                        centering_score = 1 - abs(text_center - page_center) / page_center
                        
                        # Position on page (0 = top, 1 = bottom)
                        page_position = y_pos / page_height
                        
                        element = {
                            'text': line_text,
                            'page': page_num,
                            'bbox': line_bbox,
                            'x_pos': x_pos,
                            'y_pos': y_pos,
                            'indentation': indentation,
                            'centering_score': centering_score,
                            'page_position': page_position,
                            'text_width': text_width,
                            'text_height': text_height,
                            'flags': line_flags,
                            'is_bold': bool(line_flags & 2**4),
                            'is_italic': bool(line_flags & 2**1)
                        }
                        
                        text_elements.append(element)
        
        return text_elements
    
    def _identify_headings_by_context(self, text_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify headings using context analysis instead of font size."""
        potential_headings = []
        
        for element in text_elements:
            text = element['text']
            score = 0
            reasons = []
            
            # Skip obvious non-headings
            if self._is_obviously_not_heading(text):
                continue
            
            # Numbering pattern analysis
            numbering_score = self._analyze_numbering_patterns(text)
            if numbering_score > 0:
                score += numbering_score * 4
                reasons.append(f"numbering:{numbering_score:.2f}")
            
            # Semantic content analysis
            semantic_score = self._analyze_semantic_content(text)
            if semantic_score > 0:
                score += semantic_score * 3
                reasons.append(f"semantic:{semantic_score:.2f}")
            
            # Position and indentation analysis
            position_score = self._analyze_position_context(element)
            score += position_score * 2
            reasons.append(f"position:{position_score:.2f}")
            
            # Text characteristics
            char_score = self._analyze_text_characteristics(text, element)
            score += char_score
            reasons.append(f"characteristics:{char_score:.2f}")
            
            # Structural analysis (relationship to surrounding text)
            struct_score = self._analyze_structural_context(element, text_elements)
            score += struct_score
            reasons.append(f"structure:{struct_score:.2f}")
            
            # Apply threshold
            if score >= 4.0:  # Threshold for heading classification
                potential_headings.append({
                    'text': text,
                    'page': element['page'],
                    'element': element,
                    'score': score,
                    'reasons': reasons
                })
        
        # Sort by score and return high-confidence headings
        potential_headings.sort(key=lambda x: x['score'], reverse=True)
        
        # Additional filtering based on document structure
        filtered_headings = self._filter_by_document_structure(potential_headings)
        
        return filtered_headings
    
    def _is_obviously_not_heading(self, text: str) -> bool:
        """Check if text is obviously not a heading."""
        text_lower = text.lower().strip()
        
        # Length checks
        if len(text) < 2 or len(text) > 200:
            return True
        
        # Pattern exclusions
        exclusion_patterns = [
            r'^\d+$',  # Just numbers
            r'^page \d+',  # Page numbers
            r'^figure \d+',  # Figure captions
            r'^table \d+',  # Table captions
            r'www\.',  # URLs
            r'http',  # URLs
            r'\w+@\w+\.',  # Email addresses
            r'^\s*-+\s*$',  # Lines of dashes
            r'^\s*=+\s*$',  # Lines of equals
            r'^\.\.\.',  # Ellipsis
        ]
        
        for pattern in exclusion_patterns:
            if re.match(pattern, text_lower):
                return True
        
        # Content exclusions
        exclusions = [
            'lorem ipsum', 'this page intentionally', 'copyright', '©',
            'all rights reserved', 'confidential', 'proprietary',
            'draft', 'preliminary', 'revision', 'version'
        ]
        
        if any(excl in text_lower for excl in exclusions):
            return True
        
        return False
    
    def _analyze_numbering_patterns(self, text: str) -> float:
        """Analyze numbering patterns that indicate headings."""
        text_stripped = text.strip()
        
        # Check against numbering patterns
        for pattern in self.heading_indicators['numbering_patterns']:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return 1.0
        
        # Check for chapter/section patterns
        for pattern in self.heading_indicators['chapter_patterns']:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return 1.0
        
        # Check for numbered sections within text
        numbered_section_patterns = [
            r'^\d+\.\s+\w+',  # "1. Introduction"
            r'^chapter \d+[:\-\s]',  # "Chapter 1: Title"
            r'^section \d+[:\-\s]',  # "Section 1: Title"
            r'^part [ivxlc]+[:\-\s]',  # "Part I: Title"
            r'^article [ivxlc]+[:\-\s]',  # "Article I: Title"
        ]
        
        for pattern in numbered_section_patterns:
            if re.match(pattern, text_stripped, re.IGNORECASE):
                return 0.9
        
        # Partial matches
        if re.search(r'\d+\.\d+', text_stripped):  # Contains "x.y" pattern
            return 0.3
        
        return 0
    
    def _analyze_semantic_content(self, text: str) -> float:
        """Analyze semantic content for heading indicators."""
        text_lower = text.lower().strip()
        score = 0
        
        # Direct semantic markers
        for marker in self.heading_indicators['semantic_markers']:
            if marker in text_lower:
                score += 0.8
        
        # Structural words
        for word in self.heading_indicators['structural_words']:
            if word in text_lower:
                score += 0.5
        
        # Common heading phrases
        heading_phrases = [
            'overview', 'summary', 'introduction', 'background', 'conclusion',
            'methodology', 'results', 'discussion', 'analysis', 'implementation',
            'requirements', 'specifications', 'procedures', 'guidelines',
            'framework', 'approach', 'strategy', 'objectives', 'goals'
        ]
        
        for phrase in heading_phrases:
            if phrase in text_lower:
                score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _analyze_position_context(self, element: Dict[str, Any]) -> float:
        """Analyze position and indentation context."""
        score = 0
        
        # Indentation analysis
        indentation = element['indentation']
        
        # Left-aligned or slightly indented (typical for headings)
        if indentation < 0.5:  # Less than 0.5 inch indentation
            score += 0.5
        elif indentation > 2.0:  # Very indented (likely body text)
            score -= 0.3
        
        # Centering analysis
        centering_score = element['centering_score']
        if centering_score > 0.8:  # Well-centered (potential title)
            score += 0.4
        
        # Page position analysis
        page_position = element['page_position']
        if page_position < 0.2:  # Top of page
            score += 0.3
        elif page_position > 0.8:  # Bottom of page (less likely)
            score -= 0.2
        
        # Isolation analysis (spacing around element)
        # This would require analyzing gaps between elements
        # For now, use a simple heuristic
        
        return max(0, score)
    
    def _analyze_text_characteristics(self, text: str, element: Dict[str, Any]) -> float:
        """Analyze text characteristics that suggest headings."""
        score = 0
        
        # Length analysis
        length = len(text)
        if 5 <= length <= 100:  # Reasonable heading length
            score += 0.3
        elif length > 200:  # Too long for heading
            score -= 0.5
        
        # Capitalization analysis
        if text.isupper():
            score += 0.4
        elif text.istitle():
            score += 0.3
        
        # Punctuation analysis
        if not text.endswith('.'):  # Headings usually don't end with periods
            score += 0.2
        
        if text.endswith(':'):  # Headings sometimes end with colons
            score += 0.1
        
        # Bold/italic analysis
        if element.get('is_bold', False):
            score += 0.3
        
        if element.get('is_italic', False):
            score += 0.1
        
        # Word count analysis
        word_count = len(text.split())
        if 1 <= word_count <= 10:  # Typical heading word count
            score += 0.2
        
        return score
    
    def _analyze_structural_context(self, element: Dict[str, Any], all_elements: List[Dict[str, Any]]) -> float:
        """Analyze structural context relative to surrounding text."""
        score = 0
        current_idx = all_elements.index(element)
        
        # Look for spacing patterns (simplified)
        # In a real implementation, you'd analyze actual spacing
        
        # Check if this element is isolated (has space around it)
        if current_idx > 0 and current_idx < len(all_elements) - 1:
            prev_element = all_elements[current_idx - 1]
            next_element = all_elements[current_idx + 1]
            
            # Check Y-position gaps (simplified)
            gap_before = element['y_pos'] - prev_element['y_pos']
            gap_after = next_element['y_pos'] - element['y_pos']
            
            # Headings often have more space before and after
            if gap_before > 20:  # More space before
                score += 0.2
            if gap_after > 15:  # More space after
                score += 0.2
        
        # Check consistency with document structure
        # This is a simplified heuristic
        same_indentation_count = sum(
            1 for e in all_elements 
            if abs(e['indentation'] - element['indentation']) < 0.1
        )
        
        # If many elements have same indentation, might be a heading level
        if same_indentation_count >= 3:
            score += 0.1
        
        return score
    
    def _filter_by_document_structure(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter headings based on overall document structure."""
        if not headings:
            return []
        
        # Remove duplicates (keep highest scoring)
        seen_texts = {}
        for heading in headings:
            text_lower = heading['text'].lower().strip()
            if text_lower not in seen_texts or heading['score'] > seen_texts[text_lower]['score']:
                seen_texts[text_lower] = heading
        
        filtered = list(seen_texts.values())
        
        # Sort by page and position
        filtered.sort(key=lambda x: (x['page'], x['element']['y_pos']))
        
        return filtered
    
    def _assign_hierarchy_levels(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assign H1, H2, H3, H4 levels based on context analysis."""
        if not headings:
            return []
        
        # Analyze indentation patterns
        indentations = [h['element']['indentation'] for h in headings]
        unique_indentations = sorted(set(indentations))
        
        # Create indentation to level mapping
        indent_to_level = {}
        level_names = ['H1', 'H2', 'H3', 'H4']
        
        for i, indent in enumerate(unique_indentations[:4]):  # Only H1-H4
            indent_to_level[indent] = level_names[i]
        
        # Analyze numbering patterns for hierarchy
        numbering_hierarchy = self._analyze_numbering_hierarchy(headings)
        
        # Assign levels
        outline = []
        for heading in headings:
            element = heading['element']
            text = heading['text']
            
            # Primary: Use numbering hierarchy if available
            level = numbering_hierarchy.get(text)
            
            # Secondary: Use indentation
            if not level:
                indent = element['indentation']
                closest_indent = min(indent_to_level.keys(), key=lambda x: abs(x - indent))
                level = indent_to_level[closest_indent]
            
            # Tertiary: Use position and semantic analysis
            if not level:
                if element['centering_score'] > 0.8:
                    level = 'H1'  # Centered text likely major heading
                elif element['indentation'] < 0.25:
                    level = 'H1'
                elif element['indentation'] < 0.75:
                    level = 'H2'
                else:
                    level = 'H3'
            
            outline.append({
                "level": level,
                "text": text,
                "page": element['page'] + 1  # Convert to 1-indexed
            })
        
        return outline
    
    def _analyze_numbering_hierarchy(self, headings: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze numbering patterns to determine hierarchy."""
        numbering_levels = {}
        
        for heading in headings:
            text = heading['text'].strip()
            
            # Pattern matching for different numbering schemes
            if re.match(r'^\d+\.$', text):  # "1."
                numbering_levels[text] = 'H1'
            elif re.match(r'^\d+\.\d+$', text):  # "1.1"
                numbering_levels[text] = 'H2'
            elif re.match(r'^\d+\.\d+\.\d+$', text):  # "1.1.1"
                numbering_levels[text] = 'H3'
            elif re.match(r'^\d+\.\d+\.\d+\.\d+$', text):  # "1.1.1.1"
                numbering_levels[text] = 'H4'
            elif re.match(r'^[IVXLC]+\.$', text, re.IGNORECASE):  # Roman numerals
                numbering_levels[text] = 'H1'
            elif re.match(r'^[A-Z]\.$', text):  # "A.", "B."
                numbering_levels[text] = 'H2'
            elif re.match(r'^[a-z]\.$', text):  # "a.", "b."
                numbering_levels[text] = 'H3'
            elif re.match(r'^\d+\.\s+\w+', text):  # "1. Introduction"
                numbering_levels[text] = 'H1'
            elif re.match(r'^\d+\.\d+\s+\w+', text):  # "1.1 Background"
                numbering_levels[text] = 'H2'
            elif re.match(r'^chapter \d+', text, re.IGNORECASE):
                numbering_levels[text] = 'H1'
            elif re.match(r'^section \d+', text, re.IGNORECASE):
                numbering_levels[text] = 'H2'
        
        return numbering_levels

# Wrapper functions for compatibility
def process_dataset(input_dir: str, output_dir: str) -> None:
    """Process all PDFs in the dataset directory using context-aware extraction."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    extractor = ContextAwarePDFExtractor()
    
    # Process all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Processing {len(pdf_files)} PDF files with context-aware extraction...")
    
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
    """Test the context-aware extractor on a single PDF file."""
    extractor = ContextAwarePDFExtractor()
    result = extractor.extract_outline(pdf_path)
    
    print("\n" + "="*50)
    print(f"Context-Aware Results for: {os.path.basename(pdf_path)}")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python solution_1a_context_aware.py <pdf_file>           # Test single PDF")
        print("  python solution_1a_context_aware.py <input_dir> <output_dir>  # Process dataset")
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