#!/usr/bin/env python3
"""
Test MiniLM Solution vs Existing Methods
Comprehensive comparison of neural vs rule-based approaches
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolutionComparator:
    """Compare different PDF structure extraction solutions"""
    
    def __init__(self):
        self.results = {}
        
    def load_ground_truth(self, dataset_dir: str) -> Dict[str, Dict[str, Any]]:
        """Load ground truth data from dataset"""
        ground_truth = {}
        
        json_dir = Path(dataset_dir) / "Output.json"
        if not json_dir.exists():
            logger.error(f"Ground truth directory not found: {json_dir}")
            return ground_truth
        
        for json_file in json_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Convert to consistent format
            ground_truth[json_file.stem] = {
                'title': data.get('title', ''),
                'outline': data.get('outline', [])
            }
        
        return ground_truth
    
    def run_solution(self, solution_name: str, pdf_dir: str, 
                    command_template: str) -> Dict[str, Dict[str, Any]]:
        """Run a solution on all PDFs in directory"""
        logger.info(f"Running {solution_name} solution...")
        
        results = {}
        pdf_path = Path(pdf_dir)
        
        if not pdf_path.exists():
            logger.error(f"PDF directory not found: {pdf_dir}")
            return results
        
        # Create temporary output directory
        temp_output = f"temp_output_{solution_name}"
        os.makedirs(temp_output, exist_ok=True)
        
        try:
            pdf_files = list(pdf_path.glob("*.pdf"))
            
            for pdf_file in pdf_files:
                start_time = time.time()
                
                # Run solution
                if solution_name == "minilm":
                    # Special handling for MiniLM solution
                    if os.path.exists("trained_minilm_model"):
                        from solution_1a_minilm import extract_pdf_structure
                        try:
                            result = extract_pdf_structure(str(pdf_file))
                            results[pdf_file.stem] = result
                        except Exception as e:
                            logger.error(f"MiniLM failed on {pdf_file.name}: {e}")
                            results[pdf_file.stem] = {"title": "", "outline": []}
                    else:
                        logger.warning("MiniLM model not found, skipping...")
                        continue
                
                elif solution_name == "context_aware":
                    # Run context-aware solution
                    try:
                        from solution_1a_context_aware import extract_pdf_structure
                        result = extract_pdf_structure(str(pdf_file))
                        results[pdf_file.stem] = result
                    except Exception as e:
                        logger.error(f"Context-aware failed on {pdf_file.name}: {e}")
                        results[pdf_file.stem] = {"title": "", "outline": []}
                
                elif solution_name == "font_based":
                    # Run font-based solution
                    try:
                        from solution_1a import extract_pdf_structure
                        result = extract_pdf_structure(str(pdf_file))
                        results[pdf_file.stem] = result
                    except Exception as e:
                        logger.error(f"Font-based failed on {pdf_file.name}: {e}")
                        results[pdf_file.stem] = {"title": "", "outline": []}
                
                processing_time = time.time() - start_time
                if pdf_file.stem in results:
                    results[pdf_file.stem]['processing_time'] = processing_time
        
        finally:
            # Clean up temporary directory
            import shutil
            if os.path.exists(temp_output):
                shutil.rmtree(temp_output)
        
        return results
    
    def calculate_metrics(self, predicted: Dict[str, Any], 
                         ground_truth: Dict[str, Any]) -> Dict[str, float]:
        """Calculate accuracy metrics"""
        
        # Title accuracy
        title_correct = 1 if predicted.get('title', '').strip() == ground_truth.get('title', '').strip() else 0
        
        # Outline accuracy
        pred_outline = predicted.get('outline', [])
        true_outline = ground_truth.get('outline', [])
        
        if not true_outline:
            outline_accuracy = 1.0 if not pred_outline else 0.0
        else:
            # Match headings by level and text
            correct_headings = 0
            for true_heading in true_outline:
                for pred_heading in pred_outline:
                    if (pred_heading.get('level') == true_heading.get('level') and 
                        pred_heading.get('text', '').strip() == true_heading.get('text', '').strip()):
                        correct_headings += 1
                        break
            
            outline_accuracy = correct_headings / len(true_outline)
        
        # Overall accuracy
        total_elements = 1 + len(true_outline)  # title + headings
        correct_elements = title_correct + (outline_accuracy * len(true_outline))
        overall_accuracy = correct_elements / total_elements if total_elements > 0 else 0
        
        return {
            'title_accuracy': title_correct,
            'outline_accuracy': outline_accuracy,
            'overall_accuracy': overall_accuracy,
            'total_headings': len(true_outline),
            'predicted_headings': len(pred_outline)
        }
    
    def evaluate_solution(self, solution_name: str, predictions: Dict[str, Dict[str, Any]], 
                         ground_truth: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a solution against ground truth"""
        
        title_correct = 0
        title_total = 0
        outline_correct = 0
        outline_total = 0
        total_processing_time = 0
        
        document_metrics = {}
        
        for doc_id in ground_truth:
            if doc_id not in predictions:
                continue
            
            pred = predictions[doc_id]
            truth = ground_truth[doc_id]
            
            metrics = self.calculate_metrics(pred, truth)
            document_metrics[doc_id] = metrics
            
            # Aggregate metrics
            title_correct += metrics['title_accuracy']
            title_total += 1
            
            outline_correct += metrics['outline_accuracy'] * metrics['total_headings']
            outline_total += metrics['total_headings']
            
            if 'processing_time' in pred:
                total_processing_time += pred['processing_time']
        
        # Calculate overall metrics
        title_accuracy = title_correct / title_total if title_total > 0 else 0
        outline_accuracy = outline_correct / outline_total if outline_total > 0 else 0
        overall_accuracy = (title_correct + outline_correct) / (title_total + outline_total) if (title_total + outline_total) > 0 else 0
        avg_processing_time = total_processing_time / len(document_metrics) if document_metrics else 0
        
        return {
            'solution_name': solution_name,
            'title_accuracy': title_accuracy,
            'outline_accuracy': outline_accuracy,
            'overall_accuracy': overall_accuracy,
            'documents_processed': len(document_metrics),
            'total_documents': len(ground_truth),
            'avg_processing_time': avg_processing_time,
            'document_metrics': document_metrics
        }
    
    def run_comprehensive_comparison(self):
        """Run comprehensive comparison across all datasets and solutions"""
        
        datasets = [
            ("Original", "Datasets"),
            ("Synthetic", "SyntheticDataset"),
            ("Complex", "ComplexDataset")
        ]
        
        solutions = [
            ("Font-Based", "font_based"),
            ("Context-Aware", "context_aware"),
            ("MiniLM", "minilm")
        ]
        
        all_results = {}
        
        for dataset_name, dataset_dir in datasets:
            if not os.path.exists(dataset_dir):
                logger.warning(f"Dataset {dataset_name} not found at {dataset_dir}")
                continue
            
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing on {dataset_name} Dataset")
            logger.info(f"{'='*50}")
            
            # Load ground truth
            ground_truth = self.load_ground_truth(dataset_dir)
            
            if not ground_truth:
                logger.warning(f"No ground truth found for {dataset_name}")
                continue
            
            pdf_dir = f"{dataset_dir}/Pdfs"
            dataset_results = {}
            
            for solution_name, solution_code in solutions:
                try:
                    logger.info(f"\nTesting {solution_name}...")
                    
                    # Run solution
                    predictions = self.run_solution(solution_code, pdf_dir, "")
                    
                    if not predictions:
                        logger.warning(f"No predictions from {solution_name}")
                        continue
                    
                    # Evaluate
                    evaluation = self.evaluate_solution(solution_name, predictions, ground_truth)
                    dataset_results[solution_name] = evaluation
                    
                    # Print results
                    logger.info(f"{solution_name} Results:")
                    logger.info(f"  Title Accuracy: {evaluation['title_accuracy']:.3f}")
                    logger.info(f"  Outline Accuracy: {evaluation['outline_accuracy']:.3f}")
                    logger.info(f"  Overall Accuracy: {evaluation['overall_accuracy']:.3f}")
                    logger.info(f"  Avg Processing Time: {evaluation['avg_processing_time']:.3f}s")
                
                except Exception as e:
                    logger.error(f"Failed to test {solution_name}: {e}")
            
            all_results[dataset_name] = dataset_results
        
        # Save comprehensive results
        self._save_comparison_results(all_results)
        self._print_final_summary(all_results)
        
        return all_results
    
    def _save_comparison_results(self, results: Dict[str, Any]):
        """Save comparison results to JSON"""
        output_file = "minilm_comparison_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Detailed results saved to {output_file}")
    
    def _print_final_summary(self, results: Dict[str, Any]):
        """Print final summary of all results"""
        
        print(f"\n{'='*80}")
        print("FINAL COMPARISON SUMMARY")
        print(f"{'='*80}")
        
        # Create summary table
        print(f"{'Dataset':<12} {'Solution':<15} {'Title':<8} {'Outline':<8} {'Overall':<8} {'Time(s)':<8}")
        print("-" * 80)
        
        for dataset_name, dataset_results in results.items():
            for solution_name, metrics in dataset_results.items():
                print(f"{dataset_name:<12} {solution_name:<15} "
                      f"{metrics['title_accuracy']:.3f}    "
                      f"{metrics['outline_accuracy']:.3f}    "
                      f"{metrics['overall_accuracy']:.3f}    "
                      f"{metrics['avg_processing_time']:.3f}")
        
        print(f"\n{'='*80}")
        
        # Find best performing solution overall
        best_solutions = {}
        for dataset_name, dataset_results in results.items():
            if dataset_results:
                best_solution = max(dataset_results.items(), 
                                  key=lambda x: x[1]['overall_accuracy'])
                best_solutions[dataset_name] = best_solution
        
        print("BEST PERFORMERS BY DATASET:")
        for dataset_name, (solution_name, metrics) in best_solutions.items():
            print(f"{dataset_name}: {solution_name} ({metrics['overall_accuracy']:.3f} accuracy)")

def main():
    """Main comparison function"""
    logger.info("Starting comprehensive solution comparison...")
    
    comparator = SolutionComparator()
    results = comparator.run_comprehensive_comparison()
    
    logger.info("Comparison complete!")

if __name__ == "__main__":
    main() 