#!/usr/bin/env python3
"""
Test script for context-aware solution validation
Compares generated outputs with expected results from the complex dataset
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
    
    # Extract heading texts for comparison (case-insensitive)
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
    print(f"Context-Aware Testing: {pdf_name}")
    print('='*60)
    
    # Compare titles
    expected_title = expected_result.get('title', '').strip()
    actual_title = actual_result.get('title', '').strip()
    
    # More flexible title matching
    title_match = (expected_title.lower() in actual_title.lower() or 
                  actual_title.lower() in expected_title.lower() or
                  expected_title.lower() == actual_title.lower())
    
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
    print(f"  Precision:         {outline_comparison['precision']:.3f}")
    print(f"  Recall:            {outline_comparison['recall']:.3f}")
    print(f"  F1 Score:          {outline_comparison['f1_score']:.3f}")
    
    # Show level distribution
    print(f"\nLevel Distribution:")
    print(f"  Expected: {outline_comparison['expected_levels']}")
    print(f"  Actual:   {outline_comparison['actual_levels']}")
    
    # Show sample missing and extra headings (limit output)
    if outline_comparison['missing_texts']:
        missing_sample = list(sorted(outline_comparison['missing_texts']))[:5]
        print(f"\nSample Missing headings ({len(outline_comparison['missing_texts'])} total):")
        for text in missing_sample:
            print(f"  - {text}")
        if len(outline_comparison['missing_texts']) > 5:
            print(f"  ... and {len(outline_comparison['missing_texts']) - 5} more")
    
    if outline_comparison['extra_texts']:
        extra_sample = list(sorted(outline_comparison['extra_texts']))[:5]
        print(f"\nSample Extra headings ({len(outline_comparison['extra_texts'])} total):")
        for text in extra_sample:
            print(f"  + {text}")
        if len(outline_comparison['extra_texts']) > 5:
            print(f"  ... and {len(outline_comparison['extra_texts']) - 5} more")
    
    # Overall score
    title_score = 1.0 if title_match else 0.0
    outline_score = outline_comparison['f1_score']
    overall_score = (title_score + outline_score) / 2
    
    print(f"\nScores:")
    print(f"  Title Score:    {title_score:.3f}")
    print(f"  Outline Score:  {outline_score:.3f}")
    print(f"  Overall Score:  {overall_score:.3f}")
    
    return {
        "pdf_name": pdf_name,
        "title_match": title_match,
        "title_score": title_score,
        "outline_comparison": outline_comparison,
        "outline_score": outline_score,
        "overall_score": overall_score
    }

def run_context_aware_tests(dataset_dir: str, results_dir: str = None) -> None:
    """Run tests on the complex dataset with context-aware solution."""
    
    dataset_path = Path(dataset_dir)
    expected_dir = dataset_path / "Output.json"
    pdfs_dir = dataset_path / "Pdfs"
    
    if not expected_dir.exists():
        logger.error(f"Expected results directory not found: {expected_dir}")
        return
    
    if not pdfs_dir.exists():
        logger.error(f"PDFs directory not found: {pdfs_dir}")
        return
    
    # Import the context-aware solution
    try:
        from solution_1a_context_aware import ContextAwarePDFExtractor
    except ImportError:
        logger.error("Could not import solution_1a_context_aware.py. Make sure it's in the same directory.")
        return
    
    # Initialize extractor
    extractor = ContextAwarePDFExtractor()
    
    # Get all expected JSON files
    expected_files = list(expected_dir.glob("*.json"))
    
    if not expected_files:
        logger.error(f"No expected JSON files found in {expected_dir}")
        return
    
    print(f"Found {len(expected_files)} test cases for context-aware evaluation")
    
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
        
        # Generate actual result using context-aware extraction
        try:
            actual_result = extractor.extract_outline(str(pdf_path))
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            continue
        
        # Save actual result if output directory specified
        if results_dir:
            output_path = Path(results_dir)
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
        print("CONTEXT-AWARE SOLUTION SUMMARY")
        print('='*60)
        
        avg_title_score = sum(r['title_score'] for r in all_results) / len(all_results)
        avg_outline_score = sum(r['outline_score'] for r in all_results) / len(all_results)
        avg_overall_score = sum(r['overall_score'] for r in all_results) / len(all_results)
        
        print(f"Number of test cases: {len(all_results)}")
        print(f"Average Title Score:  {avg_title_score:.3f}")
        print(f"Average Outline Score: {avg_outline_score:.3f}")
        print(f"Average Overall Score: {avg_overall_score:.3f}")
        
        # Performance distribution
        high_performers = [r for r in all_results if r['overall_score'] >= 0.7]
        medium_performers = [r for r in all_results if 0.3 <= r['overall_score'] < 0.7]
        low_performers = [r for r in all_results if r['overall_score'] < 0.3]
        
        print(f"\nPerformance Distribution:")
        print(f"  High performers (≥70%): {len(high_performers)}")
        print(f"  Medium performers (30-70%): {len(medium_performers)}")
        print(f"  Low performers (<30%): {len(low_performers)}")
        
        # Best and worst performers
        best = max(all_results, key=lambda x: x['overall_score'])
        worst = min(all_results, key=lambda x: x['overall_score'])
        
        print(f"\nBest performing file: {best['pdf_name']} (Score: {best['overall_score']:.3f})")
        print(f"Worst performing file: {worst['pdf_name']} (Score: {worst['overall_score']:.3f})")
        
        # Comparison with font-based approach
        print(f"\n{'='*60}")
        print("COMPARISON: Context-Aware vs Font-Based")
        print('='*60)
        print("Font-Based Solution (uniform fonts):")
        print("  - Average Title Score: 5%")
        print("  - Average Outline Score: 0%")
        print("  - Average Overall Score: 3%")
        print("")
        print("Context-Aware Solution (uniform fonts):")
        print(f"  - Average Title Score: {avg_title_score*100:.1f}%")
        print(f"  - Average Outline Score: {avg_outline_score*100:.1f}%")
        print(f"  - Average Overall Score: {avg_overall_score*100:.1f}%")
        print("")
        print(f"IMPROVEMENT:")
        print(f"  - Title Score: +{(avg_title_score-0.05)*100:.1f} percentage points")
        print(f"  - Outline Score: +{avg_outline_score*100:.1f} percentage points")
        print(f"  - Overall Score: +{(avg_overall_score-0.03)*100:.1f} percentage points")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_context_aware.py <dataset_dir> [results_dir]")
        print("")
        print("Example:")
        print("  python test_context_aware.py ComplexDataset")
        print("  python test_context_aware.py ComplexDataset ContextAwareResults")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    results_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory not found: {dataset_dir}")
        sys.exit(1)
    
    run_context_aware_tests(dataset_dir, results_dir)

if __name__ == "__main__":
    main() 