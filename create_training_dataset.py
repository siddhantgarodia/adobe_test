#!/usr/bin/env python3
"""
Create Training Dataset for Neural PDF Structure Extraction
Generates a large dataset with both positive and negative examples for training
"""

import os
import json
import random
from pathlib import Path
import PyPDF2
from typing import Dict, List, Tuple, Any
import re

class TrainingDatasetGenerator:
    def __init__(self):
        self.generated_docs = 0
        self.total_samples = 0
        
        # Expanded vocabularies for more diverse training data
        self.technical_vocab = {
            'prefixes': ['Advanced', 'Comprehensive', 'Technical', 'Professional', 'Industrial', 'Scientific', 'Engineering', 'Digital', 'Modern', 'Innovative'],
            'domains': ['Software Engineering', 'Machine Learning', 'Data Science', 'Cybersecurity', 'Cloud Computing', 'DevOps', 'AI Research', 'Blockchain', 'IoT Systems', 'Quantum Computing'],
            'suffixes': ['Manual', 'Guide', 'Handbook', 'Documentation', 'Protocol', 'Framework', 'Specification', 'Standards', 'Best Practices', 'Implementation Guide']
        }
        
        self.business_vocab = {
            'prefixes': ['Strategic', 'Corporate', 'Executive', 'Annual', 'Quarterly', 'Financial', 'Market', 'Business', 'Operational', 'Performance'],
            'domains': ['Analysis Report', 'Business Plan', 'Market Research', 'Financial Statement', 'Risk Assessment', 'Compliance Manual', 'Policy Document', 'Audit Report', 'Investment Strategy', 'Performance Review'],
            'suffixes': ['2024', '2025', 'Executive Summary', 'Detailed Analysis', 'Final Report', 'Draft Version', 'Revised Edition', 'Updated Guidelines']
        }
        
        self.academic_vocab = {
            'prefixes': ['Research', 'Academic', 'Scholarly', 'Theoretical', 'Empirical', 'Experimental', 'Comparative', 'Longitudinal', 'Cross-sectional', 'Meta-analysis'],
            'domains': ['Computer Science', 'Psychology', 'Biology', 'Physics', 'Mathematics', 'Economics', 'Sociology', 'Medicine', 'Environmental Science', 'Neuroscience'],
            'suffixes': ['Thesis', 'Dissertation', 'Research Paper', 'Study Results', 'Literature Review', 'Case Study', 'Field Report', 'Lab Report', 'Conference Paper', 'Journal Article']
        }

    def generate_training_documents(self, num_docs: int = 100) -> Dict[str, Any]:
        """Generate a large number of training documents"""
        
        training_data = {
            'documents': [],
            'metadata': {
                'total_documents': num_docs,
                'total_samples': 0,
                'label_distribution': {
                    'Title': 0,
                    'H1': 0, 
                    'H2': 0,
                    'H3': 0,
                    'H4': 0,
                    'None': 0
                }
            }
        }
        
        for i in range(num_docs):
            doc_data = self._generate_single_document(f"TRAIN_{i+1:03d}")
            training_data['documents'].append(doc_data)
            
            # Update metadata
            for sample in doc_data['samples']:
                label = sample['label']
                training_data['metadata']['label_distribution'][label] += 1
                training_data['metadata']['total_samples'] += 1
        
        return training_data

    def _generate_single_document(self, doc_id: str) -> Dict[str, Any]:
        """Generate a single document with comprehensive text samples"""
        
        # Choose document type
        doc_type = random.choice(['technical', 'business', 'academic', 'legal', 'medical', 'scientific', 'manual', 'report'])
        
        # Generate title and outline structure
        title = self._generate_title(doc_type)
        outline = self._generate_detailed_outline(doc_type)
        
        # Generate comprehensive text content with negative examples
        samples = []
        
        # Add title sample
        samples.append({
            'text': title,
            'label': 'Title',
            'features': self._extract_features(title, 'title')
        })
        
        # Add heading samples
        for heading in outline:
            samples.append({
                'text': heading['text'],
                'label': heading['level'],
                'features': self._extract_features(heading['text'], 'heading', heading['level'])
            })
        
        # Generate negative examples (regular paragraphs, captions, etc.)
        negative_samples = self._generate_negative_examples(doc_type, len(outline) * 3)
        for text in negative_samples:
            samples.append({
                'text': text,
                'label': 'None',
                'features': self._extract_features(text, 'paragraph')
            })
        
        return {
            'document_id': doc_id,
            'title': title,
            'outline': outline,
            'samples': samples,
            'document_type': doc_type
        }

    def _generate_title(self, doc_type: str) -> str:
        """Generate realistic document titles"""
        if doc_type == 'technical':
            vocab = self.technical_vocab
        elif doc_type == 'business':
            vocab = self.business_vocab
        elif doc_type == 'academic':
            vocab = self.academic_vocab
        else:
            # Default mixed vocabulary
            vocab = random.choice([self.technical_vocab, self.business_vocab, self.academic_vocab])
        
        prefix = random.choice(vocab['prefixes'])
        domain = random.choice(vocab['domains'])
        suffix = random.choice(vocab['suffixes'])
        
        return f"{prefix} {domain} {suffix}"

    def _generate_detailed_outline(self, doc_type: str) -> List[Dict[str, Any]]:
        """Generate detailed outline with many headings"""
        outline = []
        page_num = 1
        
        # Generate more headings for better training
        num_h1 = random.randint(8, 15)
        
        for i in range(num_h1):
            # H1 headings
            h1_text = self._generate_heading_text(doc_type, 'H1', i+1)
            outline.append({'level': 'H1', 'text': h1_text, 'page': page_num})
            page_num += random.randint(1, 3)
            
            # H2 headings under this H1
            num_h2 = random.randint(2, 5)
            for j in range(num_h2):
                h2_text = self._generate_heading_text(doc_type, 'H2', i+1, j+1)
                outline.append({'level': 'H2', 'text': h2_text, 'page': page_num})
                page_num += random.randint(0, 2)
                
                # H3 headings under this H2
                if random.random() < 0.6:  # 60% chance of H3
                    num_h3 = random.randint(1, 3)
                    for k in range(num_h3):
                        h3_text = self._generate_heading_text(doc_type, 'H3', i+1, j+1, k+1)
                        outline.append({'level': 'H3', 'text': h3_text, 'page': page_num})
                        page_num += random.randint(0, 1)
                        
                        # H4 headings under this H3
                        if random.random() < 0.4:  # 40% chance of H4
                            num_h4 = random.randint(1, 2)
                            for l in range(num_h4):
                                h4_text = self._generate_heading_text(doc_type, 'H4', i+1, j+1, k+1, l+1)
                                outline.append({'level': 'H4', 'text': h4_text, 'page': page_num})
                                page_num += random.randint(0, 1)
        
        return outline

    def _generate_heading_text(self, doc_type: str, level: str, *numbers) -> str:
        """Generate realistic heading text"""
        heading_patterns = {
            'technical': {
                'H1': ['Introduction', 'System Architecture', 'Implementation', 'Testing', 'Deployment', 'Security', 'Performance', 'Maintenance', 'API Reference', 'Troubleshooting'],
                'H2': ['Overview', 'Requirements', 'Design Patterns', 'Configuration', 'Installation', 'Usage', 'Examples', 'Best Practices', 'Common Issues', 'Updates'],
                'H3': ['Prerequisites', 'Step-by-step Guide', 'Code Examples', 'Error Handling', 'Optimization', 'Validation', 'Testing Procedures', 'Documentation'],
                'H4': ['Detailed Steps', 'Code Snippets', 'Parameter Details', 'Return Values', 'Edge Cases', 'Performance Tips', 'Debug Information']
            },
            'business': {
                'H1': ['Executive Summary', 'Market Analysis', 'Financial Projections', 'Risk Assessment', 'Strategic Planning', 'Operations', 'Human Resources', 'Technology', 'Compliance'],
                'H2': ['Current Situation', 'Market Trends', 'Revenue Streams', 'Cost Structure', 'SWOT Analysis', 'Competitive Landscape', 'Growth Strategy', 'Implementation Plan'],
                'H3': ['Key Metrics', 'Performance Indicators', 'Budget Allocation', 'Timeline', 'Resource Requirements', 'Success Criteria', 'Monitoring Procedures'],
                'H4': ['Specific Actions', 'Milestones', 'Deliverables', 'Responsibilities', 'Review Process', 'Reporting Structure']
            }
        }
        
        patterns = heading_patterns.get(doc_type, heading_patterns['technical'])
        base_text = random.choice(patterns[level])
        
        # Add numbering for some headings
        if random.random() < 0.7:
            if level == 'H1':
                return f"{numbers[0]}. {base_text}"
            elif level == 'H2' and len(numbers) >= 2:
                return f"{numbers[0]}.{numbers[1]} {base_text}"
            elif level == 'H3' and len(numbers) >= 3:
                return f"{numbers[0]}.{numbers[1]}.{numbers[2]} {base_text}"
            elif level == 'H4' and len(numbers) >= 4:
                return f"{numbers[0]}.{numbers[1]}.{numbers[2]}.{numbers[3]} {base_text}"
        
        return base_text

    def _generate_negative_examples(self, doc_type: str, count: int) -> List[str]:
        """Generate text that should NOT be classified as headings"""
        negative_examples = []
        
        paragraph_templates = [
            "This section provides detailed information about the implementation of the system components and their interactions.",
            "The research methodology employed in this study follows established protocols and industry best practices.",
            "According to recent market analysis, the trends indicate significant growth potential in the next quarter.",
            "The following table shows the comparison between different approaches and their respective advantages.",
            "It is important to note that all procedures must be followed strictly to ensure compliance with regulations.",
            "Figure 3.2 illustrates the relationship between various factors affecting system performance.",
            "The experimental results demonstrate a clear correlation between input parameters and output quality.",
            "Based on the analysis of collected data, several key insights can be derived for future development.",
            "The proposed solution addresses the main challenges identified during the initial assessment phase.",
            "Copyright © 2024 Company Name. All rights reserved. No part of this publication may be reproduced."
        ]
        
        for _ in range(count):
            # Choose random paragraph template and modify it
            base_text = random.choice(paragraph_templates)
            
            # Sometimes add specific domain terms
            if doc_type == 'technical':
                tech_terms = ['API', 'database', 'algorithm', 'framework', 'protocol', 'interface', 'module', 'component']
                base_text = base_text.replace('system', random.choice(tech_terms))
            elif doc_type == 'business':
                biz_terms = ['strategy', 'revenue', 'market', 'customer', 'product', 'service', 'stakeholder', 'investment']
                base_text = base_text.replace('system', random.choice(biz_terms))
            
            negative_examples.append(base_text)
        
        return negative_examples

    def _extract_features(self, text: str, text_type: str, level: str = None) -> Dict[str, Any]:
        """Extract features for machine learning"""
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_punctuation': bool(re.search(r'[.:;!?]', text)),
            'all_caps': text.isupper(),
            'title_case': text.istitle(),
            'starts_with_number': bool(re.match(r'^\d', text)),
            'has_colon': ':' in text,
            'is_short': len(text) < 50,
            'is_long': len(text) > 200,
            'text_type': text_type,
            'level': level if level else 'none'
        }
        
        return features

if __name__ == "__main__":
    generator = TrainingDatasetGenerator()
    
    print("Generating training dataset...")
    training_data = generator.generate_training_documents(num_docs=200)
    
    # Save training data
    os.makedirs('TrainingDataset', exist_ok=True)
    
    with open('TrainingDataset/training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Generated {training_data['metadata']['total_documents']} documents")
    print(f"Total samples: {training_data['metadata']['total_samples']}")
    print("Label distribution:", training_data['metadata']['label_distribution'])
    print("Training dataset saved to TrainingDataset/training_data.json") 