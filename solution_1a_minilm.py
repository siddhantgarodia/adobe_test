#!/usr/bin/env python3
"""
PDF Structure Extraction using Trained MiniLM Model
Adobe Hackathon 2025 - Problem 1(a) - Neural Solution
"""

import os
import json
import re
from pathlib import Path
import PyPDF2
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Any, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiniLMPDFExtractor:
    """PDF structure extractor using trained MiniLM model"""
    
    def __init__(self, model_path: str = "trained_minilm_model"):
        """Initialize with trained model"""
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.label_mapping = None
        
        if os.path.exists(model_path):
            self._load_model()
        else:
            logger.warning(f"Model not found at {model_path}. Please train the model first.")
    
    def _load_model(self):
        """Load the trained model and tokenizer"""
        logger.info(f"Loading model from {self.model_path}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            
            # Load label mappings
            with open(f"{self.model_path}/label_mapping.json", 'r') as f:
                self.label_mapping = json.load(f)
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict_text_type(self, text: str) -> Tuple[str, float]:
        """Predict if text is Title, H1, H2, H3, H4, or None"""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded")
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        predicted_id = torch.argmax(predictions, dim=-1).item()
        confidence = predictions[0][predicted_id].item()
        
        predicted_label = self.label_mapping['id_to_label'][str(predicted_id)]
        
        return predicted_label, confidence
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract all text elements from PDF with position info"""
        text_elements = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text_content = page.extract_text()
                    
                    if text_content:
                        # Split into lines and clean
                        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                        
                        for line_num, line in enumerate(lines):
                            # Skip very short lines (likely artifacts)
                            if len(line) < 3:
                                continue
                            
                            text_elements.append({
                                'text': line,
                                'page': page_num,
                                'line_num': line_num,
                                'length': len(line),
                                'word_count': len(line.split())
                            })
        
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise
        
        return text_elements
    
    def extract_structure(self, pdf_path: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Extract document structure using MiniLM model"""
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Extracting structure from {pdf_path}")
        
        # Extract all text elements
        text_elements = self.extract_text_from_pdf(pdf_path)
        
        if not text_elements:
            return {"title": "", "outline": []}
        
        # Classify each text element
        classified_elements = []
        for element in text_elements:
            prediction, confidence = self.predict_text_type(element['text'])
            
            element['prediction'] = prediction
            element['confidence'] = confidence
            element['is_confident'] = confidence >= confidence_threshold
            
            classified_elements.append(element)
        
        # Extract title and outline
        title = self._extract_title(classified_elements, confidence_threshold)
        outline = self._extract_outline(classified_elements, confidence_threshold)
        
        result = {
            "title": title,
            "outline": outline
        }
        
        logger.info(f"Extracted title: {title}")
        logger.info(f"Extracted {len(outline)} headings")
        
        return result
    
    def _extract_title(self, classified_elements: List[Dict[str, Any]], 
                      confidence_threshold: float) -> str:
        """Extract document title from classified elements"""
        
        # Find elements predicted as Title with high confidence
        title_candidates = [
            elem for elem in classified_elements 
            if elem['prediction'] == 'Title' and elem['confidence'] >= confidence_threshold
        ]
        
        if title_candidates:
            # Choose the first high-confidence title
            best_title = title_candidates[0]
            return best_title['text']
        
        # Fallback: Look for title-like elements on first page
        first_page_elements = [elem for elem in classified_elements if elem['page'] == 1]
        
        # Try elements with decent confidence for Title
        title_candidates = [
            elem for elem in first_page_elements 
            if elem['prediction'] == 'Title' and elem['confidence'] >= 0.5
        ]
        
        if title_candidates:
            return title_candidates[0]['text']
        
        # Last fallback: Use heuristics on first page
        for elem in first_page_elements[:5]:  # Check first 5 elements
            text = elem['text']
            # Look for title-like characteristics
            if (elem['word_count'] >= 3 and elem['word_count'] <= 15 and 
                not text.startswith(('Figure', 'Table', 'Page', 'Copyright'))):
                return text
        
        return ""
    
    def _extract_outline(self, classified_elements: List[Dict[str, Any]], 
                        confidence_threshold: float) -> List[Dict[str, Any]]:
        """Extract outline from classified elements"""
        
        outline = []
        
        # Filter for heading predictions with sufficient confidence
        heading_elements = [
            elem for elem in classified_elements 
            if elem['prediction'] in ['H1', 'H2', 'H3', 'H4'] and 
               elem['confidence'] >= confidence_threshold
        ]
        
        # If we don't have enough confident predictions, lower the threshold
        if len(heading_elements) < 5:
            heading_elements = [
                elem for elem in classified_elements 
                if elem['prediction'] in ['H1', 'H2', 'H3', 'H4'] and 
                   elem['confidence'] >= 0.5
            ]
        
        # Further fallback for documents with very few headings
        if len(heading_elements) < 3:
            heading_elements = [
                elem for elem in classified_elements 
                if elem['prediction'] in ['H1', 'H2', 'H3', 'H4'] and 
                   elem['confidence'] >= 0.3
            ]
        
        # Sort by page and line number
        heading_elements.sort(key=lambda x: (x['page'], x['line_num']))
        
        # Build outline
        for elem in heading_elements:
            outline.append({
                "level": elem['prediction'],
                "text": elem['text'],
                "page": elem['page']
            })
        
        # Post-process outline to ensure logical hierarchy
        outline = self._post_process_outline(outline)
        
        return outline
    
    def _post_process_outline(self, outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process outline to fix hierarchy issues"""
        
        if not outline:
            return outline
        
        # Fix hierarchy jumps (e.g., H1 directly to H3)
        processed_outline = []
        last_level_num = 0
        
        for item in outline:
            level_num = int(item['level'][1])  # Extract number from H1, H2, etc.
            
            # If we skip levels, adjust to a logical progression
            if level_num > last_level_num + 1:
                # Don't jump more than one level
                adjusted_level_num = min(level_num, last_level_num + 1)
                item['level'] = f"H{adjusted_level_num}"
                level_num = adjusted_level_num
            
            processed_outline.append(item)
            last_level_num = level_num
        
        return processed_outline

def extract_pdf_structure(pdf_path: str, model_path: str = "trained_minilm_model") -> Dict[str, Any]:
    """Main function to extract PDF structure using MiniLM model"""
    
    extractor = MiniLMPDFExtractor(model_path)
    return extractor.extract_structure(pdf_path)

def process_multiple_pdfs(input_dir: str, output_dir: str, 
                         model_path: str = "trained_minilm_model"):
    """Process multiple PDFs and save results"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    extractor = MiniLMPDFExtractor(model_path)
    
    pdf_files = list(input_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    results = {}
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing {pdf_file.name}")
            
            # Extract structure
            structure = extractor.extract_structure(str(pdf_file))
            
            # Save result
            output_file = output_path / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structure, f, indent=2, ensure_ascii=False)
            
            results[pdf_file.name] = {
                'success': True,
                'title_found': bool(structure['title']),
                'headings_found': len(structure['outline'])
            }
            
            logger.info(f"Processed {pdf_file.name}: Title={'✓' if structure['title'] else '✗'}, "
                       f"Headings={len(structure['outline'])}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {e}")
            results[pdf_file.name] = {
                'success': False,
                'error': str(e)
            }
    
    # Save processing summary
    summary_file = output_path / "processing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Processing complete. Results saved to {output_dir}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python solution_1a_minilm.py <pdf_path> [model_path]")
        print("   or: python solution_1a_minilm.py --batch <input_dir> <output_dir> [model_path]")
        sys.exit(1)
    
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 4:
            print("Batch mode requires input_dir and output_dir")
            sys.exit(1)
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3]
        model_path = sys.argv[4] if len(sys.argv) > 4 else "trained_minilm_model"
        
        results = process_multiple_pdfs(input_dir, output_dir, model_path)
        
    else:
        pdf_path = sys.argv[1]
        model_path = sys.argv[2] if len(sys.argv) > 2 else "trained_minilm_model"
        
        try:
            result = extract_pdf_structure(pdf_path, model_path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            sys.exit(1) 