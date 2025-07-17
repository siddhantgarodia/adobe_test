#!/usr/bin/env python3
"""
Test script for Problem 1(a) solution validation
Compares generated outputs with expected results from the dataset
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return {}

def compare_outlines(expected: List[Dict], actual: List[Dict]) -> Dict[str, Any]:
    """Compare two outline structures and return comparison metrics."""
    
    # Basic metrics
    expected_count = len(expected)
    actual_count = len(actual)
    
    # Extract heading texts for comparison
    expected_texts = {item.get('text', '').strip().lower() for item in expected}
    actual_texts = {item.get('text', '').strip().lower() for item in actual}
    
    # Calculate overlap
    common_texts = expected_texts.intersection(actual_texts)
    
    # Level distribution comparison
    expected_levels = {}
    actual_levels = {}
    
    for item in expected:
        level = item.get('level', '')
        expected_levels[level] = expected_levels.get(level, 0) + 1
    
    for item in actual:
        level = item.get('level', '')
        actual_levels[level] = actual_levels.get(level, 0) + 1
    
    # Calculate metrics
    if expected_count > 0:
        recall = len(common_texts) / expected_count
        precision = len(common_texts) / actual_count if actual_count > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    else:
        recall = precision = f1_score = 1.0 if actual_count == 0 else 0
    
    return {
        "expected_count": expected_count,
        "actual_count": actual_count,
        "common_count": len(common_texts),
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "expected_levels": expected_levels,
        "actual_levels": actual_levels,
        "missing_texts": expected_texts - actual_texts,
        "extra_texts": actual_texts - expected_texts
    }

def test_single_file(pdf_name: str, expected_result: Dict, actual_result: Dict) -> Dict[str, Any]:
    """Test a single PDF file against expected results."""
    
    print(f"\n{'='*60}")
    print(f"Testing: {pdf_name}")
    print('='*60)
    
    # Compare titles
    expected_title = expected_result.get('title', '').strip()
    actual_title = actual_result.get('title', '').strip()
    
    title_match = expected_title.lower() == actual_title.lower()
    
    print(f"Title Comparison:")
    print(f"  Expected: '{expected_title}'")
    print(f"  Actual:   '{actual_title}'")
    print(f"  Match:    {title_match}")
    
    # Compare outlines
    expected_outline = expected_result.get('outline', [])
    actual_outline = actual_result.get('outline', [])
    
    outline_comparison = compare_outlines(expected_outline, actual_outline)
    
    print(f"\nOutline Comparison:")
    print(f"  Expected headings: {outline_comparison['expected_count']}")
    print(f"  Actual headings:   {outline_comparison['actual_count']}")
    print(f"  Common headings:   {outline_comparison['common_count']}")
    print(f"  Precision:         {outline_comparison['precision']:.2f}")
    print(f"  Recall:            {outline_comparison['recall']:.2f}")
    print(f"  F1 Score:          {outline_comparison['f1_score']:.2f}")
    
    # Show level distribution
    print(f"\nLevel Distribution:")
    print(f"  Expected: {outline_comparison['expected_levels']}")
    print(f"  Actual:   {outline_comparison['actual_levels']}")
    
    # Show missing and extra headings
    if outline_comparison['missing_texts']:
        print(f"\nMissing headings ({len(outline_comparison['missing_texts'])}):")
        for text in sorted(outline_comparison['missing_texts']):
            print(f"  - {text}")
    
    if outline_comparison['extra_texts']:
        print(f"\nExtra headings ({len(outline_comparison['extra_texts'])}):")
        for text in sorted(outline_comparison['extra_texts']):
            print(f"  + {text}")
    
    # Overall score
    title_score = 1.0 if title_match else 0.0
    outline_score = outline_comparison['f1_score']
    overall_score = (title_score + outline_score) / 2
    
    print(f"\nScores:")
    print(f"  Title Score:    {title_score:.2f}")
    print(f"  Outline Score:  {outline_score:.2f}")
    print(f"  Overall Score:  {overall_score:.2f}")
    
    return {
        "pdf_name": pdf_name,
        "title_match": title_match,
        "title_score": title_score,
        "outline_comparison": outline_comparison,
        "outline_score": outline_score,
        "overall_score": overall_score
    }

def run_tests(dataset_dir: str, test_output_dir: str = None) -> None:
    """Run tests on the dataset."""
    
    dataset_path = Path(dataset_dir)
    expected_dir = dataset_path / "Output.json"
    pdfs_dir = dataset_path / "Pdfs"
    
    if not expected_dir.exists():
        logger.error(f"Expected results directory not found: {expected_dir}")
        return
    
    if not pdfs_dir.exists():
        logger.error(f"PDFs directory not found: {pdfs_dir}")
        return
    
    # Import the solution
    try:
        from solution_1a import EnhancedPDFOutlineExtractor
    except ImportError:
        logger.error("Could not import solution_1a.py. Make sure it's in the same directory.")
        return
    
    # Initialize extractor
    extractor = EnhancedPDFOutlineExtractor()
    
    # Get all expected JSON files
    expected_files = list(expected_dir.glob("*.json"))
    
    if not expected_files:
        logger.error(f"No expected JSON files found in {expected_dir}")
        return
    
    print(f"Found {len(expected_files)} test cases")
    
    all_results = []
    
    for json_file in expected_files:
        pdf_name = json_file.stem
        pdf_path = pdfs_dir / f"{pdf_name}.pdf"
        
        if not pdf_path.exists():
            logger.warning(f"PDF file not found: {pdf_path}")
            continue
        
        # Load expected result
        expected_result = load_json_file(str(json_file))
        if not expected_result:
            continue
        
        # Generate actual result
        try:
            actual_result = extractor.extract_outline(str(pdf_path))
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            continue
        
        # Save actual result if output directory specified
        if test_output_dir:
            output_path = Path(test_output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{pdf_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(actual_result, f, indent=4, ensure_ascii=False)
        
        # Compare results
        test_result = test_single_file(pdf_name, expected_result, actual_result)
        all_results.append(test_result)
    
    # Summary statistics
    if all_results:
        print(f"\n{'='*60}")
        print("SUMMARY STATISTICS")
        print('='*60)
        
        avg_title_score = sum(r['title_score'] for r in all_results) / len(all_results)
        avg_outline_score = sum(r['outline_score'] for r in all_results) / len(all_results)
        avg_overall_score = sum(r['overall_score'] for r in all_results) / len(all_results)
        
        print(f"Number of test cases: {len(all_results)}")
        print(f"Average Title Score:  {avg_title_score:.2f}")
        print(f"Average Outline Score: {avg_outline_score:.2f}")
        print(f"Average Overall Score: {avg_overall_score:.2f}")
        
        # Best and worst performers
        best = max(all_results, key=lambda x: x['overall_score'])
        worst = min(all_results, key=lambda x: x['overall_score'])
        
        print(f"\nBest performing file: {best['pdf_name']} (Score: {best['overall_score']:.2f})")
        print(f"Worst performing file: {worst['pdf_name']} (Score: {worst['overall_score']:.2f})")
        
        # Files with perfect scores
        perfect_files = [r for r in all_results if r['overall_score'] == 1.0]
        if perfect_files:
            print(f"\nFiles with perfect scores ({len(perfect_files)}):")
            for result in perfect_files:
                print(f"  - {result['pdf_name']}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_solution_1a.py <dataset_dir> [output_dir]")
        print("")
        print("Example:")
        print("  python test_solution_1a.py Datasets")
        print("  python test_solution_1a.py Datasets test_output")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory not found: {dataset_dir}")
        sys.exit(1)
    
    run_tests(dataset_dir, output_dir)

if __name__ == "__main__":
    main() 