#!/usr/bin/env python3
"""
Synthetic Dataset Generator for Adobe Hackathon Problem 1(a)
Generates PDF documents with various structures for testing outline extraction
"""

import os
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

def install_dependencies():
    """Install required dependencies for PDF generation."""
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab for PDF generation...")
        os.system("pip install reportlab")

# Install dependencies
install_dependencies()

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class SyntheticPDFGenerator:
    """Generate synthetic PDF documents with known structure."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
        # Document templates with different structures
        self.document_templates = [
            self.generate_technical_report,
            self.generate_business_proposal,
            self.generate_academic_paper,
            self.generate_user_manual,
            self.generate_policy_document,
            self.generate_research_paper,
            self.generate_project_plan,
            self.generate_training_manual
        ]
        
        # Content pools for generating realistic text
        self.title_templates = {
            'technical': [
                "System Architecture Design for {system}",
                "Implementation Guide: {technology} Framework",
                "Performance Analysis of {application} Systems",
                "Technical Specification for {product} Development"
            ],
            'business': [
                "Strategic Business Plan for {company}",
                "Market Analysis: {industry} Sector Report",
                "Proposal for {project} Implementation", 
                "Annual Report: {organization} Performance"
            ],
            'academic': [
                "Research Study on {topic} in {field}",
                "Analysis of {phenomenon} Effects",
                "Comparative Study: {method} vs {alternative}",
                "Literature Review: {subject} Research"
            ]
        }
        
        self.heading_pools = {
            'H1': [
                "Introduction", "Background", "Methodology", "Results", "Discussion", 
                "Conclusion", "Executive Summary", "Overview", "Implementation",
                "Requirements", "Analysis", "Recommendations", "Future Work",
                "Appendix A", "Appendix B", "References", "Acknowledgments"
            ],
            'H2': [
                "Problem Statement", "Objectives", "Scope", "Assumptions", "Constraints",
                "Data Collection", "Statistical Analysis", "Key Findings", "Limitations",
                "Best Practices", "Risk Assessment", "Cost Analysis", "Timeline",
                "Quality Assurance", "Performance Metrics", "User Requirements"
            ],
            'H3': [
                "Data Sources", "Sample Selection", "Variable Definition", "Preprocessing",
                "Model Training", "Validation Results", "Error Analysis", "Optimization",
                "Implementation Details", "Configuration", "Testing Procedures",
                "Monitoring", "Maintenance", "Documentation", "Training Materials"
            ],
            'H4': [
                "Parameter Settings", "Calibration", "Validation Metrics", "Edge Cases",
                "Performance Benchmarks", "Resource Requirements", "Dependencies",
                "Installation Steps", "Configuration Files", "Troubleshooting",
                "Advanced Features", "Customization Options", "Integration Points"
            ]
        }
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for different heading levels."""
        # Title style
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='black'
        ))
        
        # Heading styles with distinct font sizes
        self.styles.add(ParagraphStyle(
            'CustomH1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor='black'
        ))
        
        self.styles.add(ParagraphStyle(
            'CustomH2',
            parent=self.styles['Heading2'], 
            fontSize=14,
            spaceBefore=16,
            spaceAfter=10,
            textColor='black'
        ))
        
        self.styles.add(ParagraphStyle(
            'CustomH3',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=8,
            textColor='black'
        ))
        
        self.styles.add(ParagraphStyle(
            'CustomH4',
            parent=self.styles['Heading4'],
            fontSize=11,
            spaceBefore=10,
            spaceAfter=6,
            textColor='black'
        ))
        
    def generate_realistic_content(self, paragraphs: int = 2) -> str:
        """Generate realistic paragraph content."""
        sentences = [
            "This section provides detailed analysis of the proposed methodology.",
            "The implementation follows industry best practices and standards.",
            "Results demonstrate significant improvement over baseline approaches.",
            "Our findings suggest that further research is warranted in this area.",
            "The proposed solution addresses key challenges identified in previous studies.",
            "Data collection procedures were designed to ensure statistical validity.",
            "Performance metrics indicate successful achievement of project objectives.",
            "Quality assurance measures were implemented throughout the development process.",
            "Stakeholder feedback was incorporated into the final design specifications.",
            "The cost-benefit analysis supports the recommended implementation approach."
        ]
        
        content = []
        for _ in range(paragraphs):
            para_length = random.randint(3, 6)
            para_sentences = random.sample(sentences, para_length)
            content.append(" ".join(para_sentences))
        
        return "\n\n".join(content)
    
    def generate_technical_report(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a technical report structure."""
        title = random.choice(self.title_templates['technical']).format(
            system=random.choice(["Cloud Computing", "Machine Learning", "IoT", "Blockchain"]),
            technology=random.choice(["Python", "React", "Docker", "Kubernetes"]),
            application=random.choice(["Web", "Mobile", "Desktop", "Enterprise"]),
            product=random.choice(["Software", "Platform", "Framework", "Tool"])
        )
        
        structure = [
            ("H1", "Executive Summary"),
            ("H1", "Introduction"),
            ("H2", "Problem Statement"),
            ("H2", "Objectives"),
            ("H1", "Technical Architecture"),
            ("H2", "System Overview"),
            ("H3", "Core Components"),
            ("H3", "Data Flow"),
            ("H2", "Implementation Details"),
            ("H3", "Development Environment"),
            ("H3", "Deployment Strategy"),
            ("H1", "Results and Analysis"),
            ("H2", "Performance Metrics"),
            ("H2", "Quality Assessment"),
            ("H1", "Conclusion"),
            ("H1", "References")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_business_proposal(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a business proposal structure."""
        title = random.choice(self.title_templates['business']).format(
            company=random.choice(["Global Solutions Inc.", "TechCorp", "InnovateCo", "FutureSys"]),
            industry=random.choice(["Technology", "Healthcare", "Finance", "Manufacturing"]),
            project=random.choice(["Digital Transformation", "Process Optimization", "Market Expansion"]),
            organization=random.choice(["Enterprise", "Corporation", "Institute", "Foundation"])
        )
        
        structure = [
            ("H1", "Executive Summary"),
            ("H1", "Company Overview"),
            ("H2", "Mission Statement"),
            ("H2", "Core Competencies"),
            ("H1", "Market Analysis"),
            ("H2", "Industry Trends"),
            ("H2", "Competitive Landscape"),
            ("H3", "Market Opportunities"),
            ("H3", "Risk Assessment"),
            ("H1", "Proposed Solution"),
            ("H2", "Approach"),
            ("H2", "Timeline"),
            ("H3", "Phase 1: Planning"),
            ("H3", "Phase 2: Implementation"),
            ("H3", "Phase 3: Evaluation"),
            ("H1", "Investment Requirements"),
            ("H2", "Budget Breakdown"),
            ("H2", "ROI Projections"),
            ("H1", "Conclusion")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_academic_paper(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate an academic paper structure."""
        title = random.choice(self.title_templates['academic']).format(
            topic=random.choice(["Neural Networks", "Climate Change", "Social Media", "Robotics"]),
            field=random.choice(["Computer Science", "Environmental Science", "Psychology", "Engineering"]),
            phenomenon=random.choice(["Learning", "Adaptation", "Evolution", "Optimization"]),
            method=random.choice(["Deep Learning", "Statistical Analysis", "Simulation", "Experimental"]),
            alternative=random.choice(["Traditional", "Classical", "Conventional", "Standard"]),
            subject=random.choice(["AI", "Sustainability", "Human Behavior", "Technology"])
        )
        
        structure = [
            ("H1", "Abstract"),
            ("H1", "Introduction"),
            ("H2", "Research Questions"),
            ("H2", "Hypotheses"),
            ("H1", "Literature Review"),
            ("H2", "Theoretical Framework"),
            ("H2", "Previous Studies"),
            ("H1", "Methodology"),
            ("H2", "Research Design"),
            ("H2", "Data Collection"),
            ("H3", "Sampling Method"),
            ("H3", "Instruments"),
            ("H2", "Data Analysis"),
            ("H1", "Results"),
            ("H2", "Descriptive Statistics"),
            ("H2", "Inferential Analysis"),
            ("H3", "Primary Findings"),
            ("H3", "Secondary Findings"),
            ("H1", "Discussion"),
            ("H2", "Interpretation"),
            ("H2", "Implications"),
            ("H2", "Limitations"),
            ("H1", "Conclusion"),
            ("H1", "References")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_user_manual(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a user manual structure."""
        product = random.choice(["Software Application", "Mobile App", "Hardware Device", "Web Platform"])
        title = f"User Manual: {product} v{random.randint(1,5)}.{random.randint(0,9)}"
        
        structure = [
            ("H1", "Getting Started"),
            ("H2", "System Requirements"),
            ("H2", "Installation Guide"),
            ("H3", "Windows Installation"),
            ("H3", "Mac Installation"),
            ("H3", "Linux Installation"),
            ("H1", "Basic Operations"),
            ("H2", "User Interface Overview"),
            ("H2", "Navigation"),
            ("H3", "Menu System"),
            ("H3", "Keyboard Shortcuts"),
            ("H1", "Features"),
            ("H2", "Core Functionality"),
            ("H3", "Data Management"),
            ("H3", "Report Generation"),
            ("H2", "Advanced Features"),
            ("H3", "Customization"),
            ("H3", "Integration"),
            ("H1", "Troubleshooting"),
            ("H2", "Common Issues"),
            ("H2", "Error Messages"),
            ("H1", "Support")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_policy_document(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a policy document structure."""
        policy_type = random.choice(["Data Privacy", "Security", "HR", "Quality Assurance"])
        title = f"{policy_type} Policy Document"
        
        structure = [
            ("H1", "Policy Overview"),
            ("H2", "Purpose"),
            ("H2", "Scope"),
            ("H1", "Definitions"),
            ("H1", "Policy Statement"),
            ("H2", "Core Principles"),
            ("H2", "Requirements"),
            ("H3", "Mandatory Procedures"),
            ("H3", "Optional Guidelines"),
            ("H1", "Implementation"),
            ("H2", "Roles and Responsibilities"),
            ("H3", "Management"),
            ("H3", "Employees"),
            ("H3", "Contractors"),
            ("H2", "Training Requirements"),
            ("H1", "Compliance"),
            ("H2", "Monitoring"),
            ("H2", "Reporting"),
            ("H1", "Enforcement"),
            ("H2", "Violations"),
            ("H2", "Disciplinary Actions"),
            ("H1", "Review and Updates")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_research_paper(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a research paper structure."""
        research_area = random.choice(["Artificial Intelligence", "Renewable Energy", "Biotechnology", "Quantum Computing"])
        title = f"Research on {research_area}: Current Trends and Future Directions"
        
        structure = [
            ("H1", "Abstract"),
            ("H1", "Introduction"),
            ("H1", "Background"),
            ("H2", "Historical Context"),
            ("H2", "Current State"),
            ("H1", "Research Methodology"),
            ("H2", "Approach"),
            ("H2", "Data Sources"),
            ("H3", "Primary Sources"),
            ("H3", "Secondary Sources"),
            ("H1", "Analysis"),
            ("H2", "Quantitative Analysis"),
            ("H3", "Statistical Methods"),
            ("H3", "Results"),
            ("H2", "Qualitative Analysis"),
            ("H3", "Thematic Analysis"),
            ("H3", "Case Studies"),
            ("H1", "Findings"),
            ("H2", "Key Discoveries"),
            ("H2", "Implications"),
            ("H1", "Future Research"),
            ("H1", "Conclusion"),
            ("H1", "Bibliography")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_project_plan(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a project plan structure."""
        project_type = random.choice(["Software Development", "Infrastructure Upgrade", "Marketing Campaign", "Research Initiative"])
        title = f"Project Plan: {project_type} Implementation"
        
        structure = [
            ("H1", "Project Overview"),
            ("H2", "Objectives"),
            ("H2", "Deliverables"),
            ("H1", "Project Scope"),
            ("H2", "Inclusions"),
            ("H2", "Exclusions"),
            ("H1", "Project Team"),
            ("H2", "Roles and Responsibilities"),
            ("H3", "Project Manager"),
            ("H3", "Technical Lead"),
            ("H3", "Development Team"),
            ("H1", "Timeline"),
            ("H2", "Phase 1: Initiation"),
            ("H3", "Requirements Gathering"),
            ("H3", "Resource Allocation"),
            ("H2", "Phase 2: Planning"),
            ("H3", "Design"),
            ("H3", "Architecture"),
            ("H2", "Phase 3: Execution"),
            ("H3", "Development"),
            ("H3", "Testing"),
            ("H2", "Phase 4: Closure"),
            ("H1", "Risk Management"),
            ("H2", "Risk Assessment"),
            ("H2", "Mitigation Strategies"),
            ("H1", "Budget"),
            ("H1", "Quality Assurance")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def generate_training_manual(self, doc_id: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a training manual structure."""
        subject = random.choice(["Software Training", "Safety Procedures", "Customer Service", "Technical Skills"])
        title = f"Training Manual: {subject} Certification Program"
        
        structure = [
            ("H1", "Introduction"),
            ("H2", "Training Objectives"),
            ("H2", "Prerequisites"),
            ("H1", "Module 1: Fundamentals"),
            ("H2", "Basic Concepts"),
            ("H3", "Key Terminology"),
            ("H3", "Core Principles"),
            ("H2", "Practical Exercises"),
            ("H1", "Module 2: Intermediate Skills"),
            ("H2", "Advanced Concepts"),
            ("H2", "Case Studies"),
            ("H3", "Scenario 1"),
            ("H3", "Scenario 2"),
            ("H1", "Module 3: Expert Level"),
            ("H2", "Complex Applications"),
            ("H2", "Problem Solving"),
            ("H3", "Troubleshooting"),
            ("H3", "Optimization"),
            ("H1", "Assessment"),
            ("H2", "Knowledge Check"),
            ("H2", "Practical Evaluation"),
            ("H1", "Certification"),
            ("H2", "Requirements"),
            ("H2", "Maintenance"),
            ("H1", "Resources"),
            ("H2", "Additional Reading"),
            ("H2", "Support Contacts")
        ]
        
        return title, self.create_outline_structure(structure)
    
    def create_outline_structure(self, structure: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Convert structure list to expected JSON format."""
        outline = []
        current_page = 1
        
        for level, text in structure:
            outline.append({
                "level": level,
                "text": text,
                "page": current_page
            })
            
            # Simulate page breaks (roughly every 3-5 headings)
            if random.random() < 0.3:
                current_page += 1
        
        return {"outline": outline}
    
    def create_pdf_document(self, title: str, structure: List[Tuple[str, str]], output_path: str) -> None:
        """Create actual PDF document with the given structure."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Add title
        if title:
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
        
        # Add content based on structure
        for level, heading_text in structure:
            # Add heading
            story.append(Paragraph(heading_text, self.styles[f'Custom{level}']))
            
            # Add some content paragraphs
            content = self.generate_realistic_content(random.randint(1, 3))
            story.append(Paragraph(content, self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Occasionally add page breaks
            if random.random() < 0.15:
                story.append(PageBreak())
        
        doc.build(story)
    
    def generate_document(self, doc_id: str, output_dir: str) -> Dict[str, Any]:
        """Generate a single synthetic document."""
        # Choose random template
        template_func = random.choice(self.document_templates)
        
        # Generate structure
        title, structure_data = template_func(doc_id)
        structure = structure_data["outline"]
        
        # Create PDF
        pdf_path = os.path.join(output_dir, "Pdfs", f"{doc_id}.pdf")
        structure_tuples = [(item["level"], item["text"]) for item in structure]
        self.create_pdf_document(title, structure_tuples, pdf_path)
        
        # Create expected JSON output
        result = {
            "title": title,
            "outline": structure
        }
        
        json_path = os.path.join(output_dir, "Output.json", f"{doc_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        return result

def generate_synthetic_dataset(num_documents: int = 20, output_dir: str = "SyntheticDataset") -> None:
    """Generate a complete synthetic dataset."""
    
    print(f"Generating {num_documents} synthetic documents...")
    
    # Create output directories
    base_path = Path(output_dir)
    pdfs_dir = base_path / "Pdfs"
    json_dir = base_path / "Output.json"
    
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    
    generator = SyntheticPDFGenerator()
    
    # Generate documents
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "num_documents": num_documents,
        "documents": []
    }
    
    for i in range(num_documents):
        doc_id = f"SYNTH_{i+1:03d}"
        print(f"Generating document {i+1}/{num_documents}: {doc_id}")
        
        try:
            result = generator.generate_document(doc_id, output_dir)
            
            doc_info = {
                "id": doc_id,
                "title": result["title"],
                "num_headings": len(result["outline"]),
                "levels": list(set(item["level"] for item in result["outline"]))
            }
            metadata["documents"].append(doc_info)
            
        except Exception as e:
            print(f"Error generating {doc_id}: {str(e)}")
    
    # Save metadata
    with open(base_path / "dataset_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    
    print(f"\nDataset generation complete!")
    print(f"Output directory: {output_dir}")
    print(f"PDFs: {len(list(pdfs_dir.glob('*.pdf')))}")
    print(f"JSON files: {len(list(json_dir.glob('*.json')))}")
    
    # Generate summary statistics
    total_headings = sum(doc["num_headings"] for doc in metadata["documents"])
    level_counts = {}
    for doc in metadata["documents"]:
        for level in doc["levels"]:
            level_counts[level] = level_counts.get(level, 0) + 1
    
    print(f"\nDataset Statistics:")
    print(f"Total headings: {total_headings}")
    print(f"Level distribution: {level_counts}")

def test_synthetic_dataset(dataset_dir: str = "SyntheticDataset") -> None:
    """Test the solution on the synthetic dataset."""
    print("\nTesting solution on synthetic dataset...")
    
    try:
        from solution_1a import EnhancedPDFOutlineExtractor
        from test_solution_1a import run_tests
        
        # Run tests
        run_tests(dataset_dir, f"{dataset_dir}/TestResults")
        
    except ImportError as e:
        print(f"Could not import solution: {e}")
        print("Make sure solution_1a.py is in the current directory")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic dataset for PDF outline extraction")
    parser.add_argument("--num-docs", type=int, default=20, help="Number of documents to generate")
    parser.add_argument("--output-dir", default="SyntheticDataset", help="Output directory")
    parser.add_argument("--test", action="store_true", help="Test solution on generated dataset")
    
    args = parser.parse_args()
    
    # Generate dataset
    generate_synthetic_dataset(args.num_docs, args.output_dir)
    
    # Test if requested
    if args.test:
        test_synthetic_dataset(args.output_dir)

if __name__ == "__main__":
    main() 