# Adobe Hackathon 2025 - Connecting the Dots Challenge
# Round 1A: PDF Structure Extraction
# Round 1B: Persona-Driven Document Intelligence

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    """
    Round 1A: Extract structured outline from PDF documents.
    Extracts title and hierarchical headings (H1, H2, H3) with page numbers.
    """
    
    def __init__(self):
        self.max_model_size = 200  # MB constraint for Round 1A
        
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured outline from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with title and outline structure
        """
        try:
            # Import required libraries (would need to be installed in Docker)
            import fitz  # PyMuPDF for PDF processing
            
            doc = fitz.open(pdf_path)
            
            # Extract title from document metadata or first page
            title = self._extract_title(doc)
            
            # Extract headings with hierarchy detection
            outline = self._extract_headings(doc)
            
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error extracting outline from {pdf_path}: {str(e)}")
            return {"title": "", "outline": []}
    
    def _extract_title(self, doc) -> str:
        """Extract document title from metadata or first page."""
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title']
        
        # Fallback: analyze first page for title-like text
        if len(doc) > 0:
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            # Look for largest font size text at top of page
            title_candidates = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["bbox"][1] < 200:  # Top of page
                                title_candidates.append({
                                    "text": span["text"].strip(),
                                    "size": span["size"],
                                    "y": span["bbox"][1]
                                })
            
            if title_candidates:
                # Sort by font size and position
                title_candidates.sort(key=lambda x: (-x["size"], x["y"]))
                return title_candidates[0]["text"]
        
        return "Untitled Document"
    
    def _extract_headings(self, doc) -> List[Dict[str, Any]]:
        """Extract hierarchical headings from document."""
        headings = []
        font_sizes = []
        
        # First pass: collect all font sizes to determine hierarchy
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_sizes.append(span["size"])
        
        # Determine heading levels based on font sizes
        unique_sizes = sorted(set(font_sizes), reverse=True)
        size_to_level = {}
        
        # Map largest sizes to heading levels
        for i, size in enumerate(unique_sizes[:3]):  # H1, H2, H3
            if i == 0:
                size_to_level[size] = "H1"
            elif i == 1:
                size_to_level[size] = "H2"
            elif i == 2:
                size_to_level[size] = "H3"
        
        # Second pass: extract headings
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_size = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            line_size = max(line_size, span["size"])
                        
                        line_text = line_text.strip()
                        
                        # Check if this could be a heading
                        if (line_size in size_to_level and 
                            len(line_text) > 0 and 
                            len(line_text) < 200 and  # Not too long
                            not line_text.endswith('.')):  # Headings usually don't end with period
                            
                            headings.append({
                                "level": size_to_level[line_size],
                                "text": line_text,
                                "page": page_num + 1
                            })
        
        return headings


class PersonaDrivenAnalyzer:
    """
    Round 1B: Persona-driven document intelligence system.
    Extracts and prioritizes relevant sections based on persona and job-to-be-done.
    """
    
    def __init__(self):
        self.max_model_size = 1000  # MB constraint for Round 1B
        
    def analyze_documents(self, document_paths: List[str], persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """
        Analyze documents based on persona and job requirements.
        
        Args:
            document_paths: List of PDF file paths
            persona: Role description with expertise and focus areas
            job_to_be_done: Concrete task the persona needs to accomplish
            
        Returns:
            Structured analysis with relevant sections and sub-sections
        """
        try:
            import fitz
            from collections import defaultdict
            
            # Extract content from all documents
            documents_content = []
            for doc_path in document_paths:
                content = self._extract_document_content(doc_path)
                documents_content.append({
                    "path": doc_path,
                    "content": content
                })
            
            # Analyze relevance based on persona and job
            relevant_sections = self._find_relevant_sections(
                documents_content, persona, job_to_be_done
            )
            
            # Extract sub-sections from most relevant sections
            sub_sections = self._extract_subsections(
                relevant_sections[:5], persona, job_to_be_done  # Top 5 sections
            )
            
            # Prepare output
            result = {
                "metadata": {
                    "documents": [os.path.basename(path) for path in document_paths],
                    "persona": persona,
                    "job_to_be_done": job_to_be_done,
                    "timestamp": datetime.now().isoformat()
                },
                "sections": relevant_sections,
                "subsections": sub_sections
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing documents: {str(e)}")
            return self._empty_result(document_paths, persona, job_to_be_done)
    
    def _extract_document_content(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract structured content from a PDF document."""
        import fitz
        
        doc = fitz.open(pdf_path)
        content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Split into sections (simple approach based on line breaks)
            sections = self._split_into_sections(text, page_num + 1)
            content.extend(sections)
        
        doc.close()
        return content
    
    def _split_into_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Split page text into logical sections."""
        sections = []
        paragraphs = text.split('\n\n')
        
        current_section = ""
        section_title = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Heuristic: if paragraph is short and doesn't end with period, might be heading
            if len(para) < 100 and not para.endswith('.') and para.isupper() or para.istitle():
                # Save previous section if exists
                if current_section:
                    sections.append({
                        "title": section_title or "Untitled Section",
                        "content": current_section.strip(),
                        "page": page_num
                    })
                
                # Start new section
                section_title = para
                current_section = ""
            else:
                current_section += para + "\n\n"
        
        # Add final section
        if current_section:
            sections.append({
                "title": section_title or "Untitled Section",
                "content": current_section.strip(),
                "page": page_num
            })
        
        return sections
    
    def _find_relevant_sections(self, documents_content: List[Dict], persona: str, job: str) -> List[Dict[str, Any]]:
        """Find and rank sections based on relevance to persona and job."""
        all_sections = []
        
        # Simple keyword-based relevance scoring
        persona_keywords = self._extract_keywords(persona.lower())
        job_keywords = self._extract_keywords(job.lower())
        
        for doc_info in documents_content:
            doc_name = os.path.basename(doc_info["path"])
            
            for section in doc_info["content"]:
                content_lower = (section["title"] + " " + section["content"]).lower()
                
                # Calculate relevance score
                persona_score = sum(1 for keyword in persona_keywords if keyword in content_lower)
                job_score = sum(2 for keyword in job_keywords if keyword in content_lower)  # Job keywords weighted higher
                
                total_score = persona_score + job_score
                
                if total_score > 0:  # Only include relevant sections
                    all_sections.append({
                        "document": doc_name,
                        "page": section["page"],
                        "section_title": section["title"],
                        "importance_rank": total_score,
                        "content": section["content"][:500] + "..." if len(section["content"]) > 500 else section["content"]
                    })
        
        # Sort by importance and return top sections
        all_sections.sort(key=lambda x: x["importance_rank"], reverse=True)
        
        # Assign rank numbers
        for i, section in enumerate(all_sections[:20]):  # Top 20 sections
            section["importance_rank"] = i + 1
        
        return all_sections[:20]
    
    def _extract_subsections(self, relevant_sections: List[Dict], persona: str, job: str) -> List[Dict[str, Any]]:
        """Extract and refine sub-sections from relevant sections."""
        subsections = []
        
        for section in relevant_sections:
            # Split content into smaller subsections
            content = section["content"]
            sentences = content.split('. ')
            
            # Group sentences into subsections
            current_subsection = ""
            subsection_count = 0
            
            for sentence in sentences:
                current_subsection += sentence + ". "
                
                # Create subsection when we have enough content
                if len(current_subsection) > 200 or sentence == sentences[-1]:
                    if current_subsection.strip():
                        subsection_count += 1
                        subsections.append({
                            "document": section["document"],
                            "page": section["page"],
                            "refined_text": current_subsection.strip(),
                            "subsection_id": f"{section['document']}_p{section['page']}_sub{subsection_count}"
                        })
                    current_subsection = ""
        
        return subsections[:50]  # Limit to top 50 subsections
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction (in practice, would use NLP libraries)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        words = text.split()
        keywords = [word.strip('.,!?()[]{}') for word in words if len(word) > 3 and word.lower() not in stop_words]
        return list(set(keywords))
    
    def _empty_result(self, document_paths: List[str], persona: str, job: str) -> Dict[str, Any]:
        """Return empty result structure in case of errors."""
        return {
            "metadata": {
                "documents": [os.path.basename(path) for path in document_paths],
                "persona": persona,
                "job_to_be_done": job,
                "timestamp": datetime.now().isoformat()
            },
            "sections": [],
            "subsections": []
        }


def process_round_1a():
    """Process Round 1A: PDF outline extraction."""
    input_dir = Path(r"C:\Users\TopG\Desktop\Pdfs")
    output_dir = Path(r"C:\Users\TopG\Desktop\test_output\test_7")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDF files in input directory
    for pdf_file in input_dir.glob("*.pdf"):
        logger.info(f"Processing {pdf_file.name} for outline extraction...")
        
        try:
            # Extract outline
            outline_result = extractor.extract_outline(str(pdf_file))
            
            # Save result
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved outline to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")


def process_round_1b():
    """Process Round 1B: Persona-driven document analysis."""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyzer = PersonaDrivenAnalyzer()
    
    # Look for configuration file with persona and job definition
    config_file = input_dir / "config.json"
    if not config_file.exists():
        logger.error("No config.json found for Round 1B processing")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        persona = config.get("persona", "")
        job_to_be_done = config.get("job_to_be_done", "")
        
        if not persona or not job_to_be_done:
            logger.error("Invalid configuration: missing persona or job_to_be_done")
            return
        
        # Get all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        pdf_paths = [str(pdf) for pdf in pdf_files]
        
        if not pdf_paths:
            logger.error("No PDF files found for processing")
            return
        
        logger.info(f"Processing {len(pdf_paths)} documents for persona analysis...")
        
        # Analyze documents
        result = analyzer.analyze_documents(pdf_paths, persona, job_to_be_done)
        
        # Save result
        output_file = output_dir / "challenge1b_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analysis to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to process Round 1B: {str(e)}")


def main():
    """Main entry point for the application."""
    # Determine which round to process based on command line arguments or file presence
    if len(sys.argv) > 1:
        round_type = sys.argv[1].lower()
    else:
        # Auto-detect based on input files
        input_dir = Path(r"C:\Users\TopG\Desktop\Pdfs")
        if (input_dir / "config.json").exists():
            round_type = "1b"
        else:
            round_type = "1a"
    
    logger.info(f"Starting Adobe Hackathon Challenge Round {round_type.upper()}")
    
    if round_type == "1a":
        process_round_1a()
    elif round_type == "1b":
        process_round_1b()
    else:
        logger.error(f"Unknown round type: {round_type}")
        sys.exit(1)
    
    logger.info("Processing completed successfully!")


if __name__ == "__main__":
    main()
