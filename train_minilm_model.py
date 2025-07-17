#!/usr/bin/env python3
"""
Train MiniLM Model for PDF Structure Extraction
Trains a lightweight transformer model for heading classification
"""

import os
import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import pickle
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFStructureDataset(Dataset):
    """PyTorch Dataset for PDF structure extraction"""
    
    def __init__(self, texts: List[str], labels: List[str], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Create label to id mapping
        self.label_to_id = {
            'Title': 0,
            'H1': 1,
            'H2': 2,
            'H3': 3,
            'H4': 4,
            'None': 5
        }
        self.id_to_label = {v: k for k, v in self.label_to_id.items()}
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.label_to_id[label], dtype=torch.long)
        }

class MiniLMTrainer:
    """Trainer for MiniLM-based PDF structure extraction"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
    def load_training_data(self, training_data_path: str) -> Tuple[List[str], List[str]]:
        """Load and prepare training data"""
        logger.info(f"Loading training data from {training_data_path}")
        
        with open(training_data_path, 'r') as f:
            data = json.load(f)
        
        texts = []
        labels = []
        
        for doc in data['documents']:
            for sample in doc['samples']:
                texts.append(sample['text'])
                labels.append(sample['label'])
        
        logger.info(f"Loaded {len(texts)} samples")
        logger.info(f"Label distribution: {pd.Series(labels).value_counts().to_dict()}")
        
        return texts, labels
    
    def prepare_model(self, num_labels: int = 6):
        """Initialize tokenizer and model"""
        logger.info(f"Preparing model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Load model for sequence classification
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels,
            problem_type="single_label_classification"
        )
        
        # Resize token embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        logger.info(f"Model loaded with {num_labels} labels")
        
    def train_model(self, texts: List[str], labels: List[str], 
                   output_dir: str = "trained_minilm_model",
                   test_size: float = 0.2, batch_size: int = 16, 
                   num_epochs: int = 10, learning_rate: float = 2e-5):
        """Train the MiniLM model"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Create datasets
        train_dataset = PDFStructureDataset(X_train, y_train, self.tokenizer)
        test_dataset = PDFStructureDataset(X_test, y_test, self.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=100,
            weight_decay=0.01,
            learning_rate=learning_rate,
            logging_dir=f'{output_dir}/logs',
            logging_steps=50,
            eval_strategy="steps",
            eval_steps=200,
            save_steps=400,
            load_best_model_at_end=True,
            metric_for_best_model="eval_accuracy",
            greater_is_better=True,
            save_total_limit=2,
            remove_unused_columns=False
        )
        
        # Custom compute metrics function
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            
            # Calculate metrics
            accuracy = accuracy_score(labels, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
            
            return {
                'accuracy': accuracy,
                'f1': f1,
                'precision': precision,
                'recall': recall
            }
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train model
        logger.info("Starting training...")
        self.trainer.train()
        
        # Evaluate on test set
        logger.info("Evaluating on test set...")
        test_results = self.trainer.evaluate(test_dataset)
        logger.info(f"Test results: {test_results}")
        
        # Detailed evaluation
        predictions = self.trainer.predict(test_dataset)
        y_pred = np.argmax(predictions.predictions, axis=1)
        
        # Convert back to label names
        label_to_id = train_dataset.label_to_id
        id_to_label = {v: k for k, v in label_to_id.items()}
        
        y_test_labels = [id_to_label[label_to_id[label]] for label in y_test]
        y_pred_labels = [id_to_label[pred] for pred in y_pred]
        
        # Print detailed classification report
        print("\nDetailed Classification Report:")
        print(classification_report(y_test_labels, y_pred_labels, target_names=list(label_to_id.keys())))
        
        return test_results
    
    def save_model(self, output_dir: str = "trained_minilm_model"):
        """Save the trained model and tokenizer"""
        logger.info(f"Saving model to {output_dir}")
        
        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save label mappings
        label_mapping = {
            'label_to_id': {
                'Title': 0, 'H1': 1, 'H2': 2, 'H3': 3, 'H4': 4, 'None': 5
            },
            'id_to_label': {
                0: 'Title', 1: 'H1', 2: 'H2', 3: 'H3', 4: 'H4', 5: 'None'
            }
        }
        
        with open(f"{output_dir}/label_mapping.json", 'w') as f:
            json.dump(label_mapping, f, indent=2)
        
        logger.info("Model saved successfully")
        
        # Check model size
        model_size = self._get_model_size(output_dir)
        logger.info(f"Model size: {model_size:.2f} MB")
        
        if model_size > 200:
            logger.warning(f"Model size ({model_size:.2f} MB) exceeds 200MB limit!")
        else:
            logger.info("Model size is within 200MB limit ✓")
    
    def _get_model_size(self, model_dir: str) -> float:
        """Calculate total model size in MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(model_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB

class ModelEvaluator:
    """Evaluate trained model performance"""
    
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        
        # Load label mappings
        with open(f"{model_dir}/label_mapping.json", 'r') as f:
            mappings = json.load(f)
        self.label_to_id = mappings['label_to_id']
        self.id_to_label = {int(k): v for k, v in mappings['id_to_label'].items()}
    
    def predict(self, text: str) -> Tuple[str, float]:
        """Predict label for a single text"""
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
        
        predicted_label = self.id_to_label[predicted_id]
        
        return predicted_label, confidence
    
    def evaluate_on_existing_datasets(self):
        """Evaluate model on existing datasets"""
        logger.info("Evaluating model on existing datasets...")
        
        # Test on complex dataset
        complex_results = self._evaluate_dataset("ComplexDataset/Output.json")
        logger.info(f"Complex dataset results: {complex_results}")
        
        # Test on synthetic dataset
        synthetic_results = self._evaluate_dataset("SyntheticDataset/Output.json")
        logger.info(f"Synthetic dataset results: {synthetic_results}")
        
        return {
            'complex_dataset': complex_results,
            'synthetic_dataset': synthetic_results
        }
    
    def _evaluate_dataset(self, dataset_dir: str) -> Dict[str, Any]:
        """Evaluate on a specific dataset"""
        import glob
        
        json_files = glob.glob(f"{dataset_dir}/*.json")
        
        title_correct = 0
        title_total = 0
        heading_correct = 0
        heading_total = 0
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Evaluate title
            title_pred, title_conf = self.predict(data['title'])
            title_total += 1
            if title_pred == 'Title':
                title_correct += 1
            
            # Evaluate headings
            for heading in data['outline']:
                heading_pred, heading_conf = self.predict(heading['text'])
                heading_total += 1
                if heading_pred == heading['level']:
                    heading_correct += 1
        
        title_accuracy = title_correct / title_total if title_total > 0 else 0
        heading_accuracy = heading_correct / heading_total if heading_total > 0 else 0
        overall_accuracy = (title_correct + heading_correct) / (title_total + heading_total) if (title_total + heading_total) > 0 else 0
        
        return {
            'title_accuracy': title_accuracy,
            'heading_accuracy': heading_accuracy,
            'overall_accuracy': overall_accuracy,
            'total_samples': title_total + heading_total
        }

def main():
    """Main training pipeline"""
    logger.info("Starting MiniLM training pipeline...")
    
    # Generate training data if not exists
    if not os.path.exists('TrainingDataset/training_data.json'):
        logger.info("Generating training dataset...")
        os.system('python create_training_dataset.py')
    
    # Initialize trainer
    trainer = MiniLMTrainer()
    
    # Load training data
    texts, labels = trainer.load_training_data('TrainingDataset/training_data.json')
    
    # Prepare model
    trainer.prepare_model()
    
    # Train model
    results = trainer.train_model(texts, labels, num_epochs=5, batch_size=8)
    
    # Save model
    trainer.save_model()
    
    # Evaluate model
    logger.info("Evaluating trained model...")
    evaluator = ModelEvaluator("trained_minilm_model")
    eval_results = evaluator.evaluate_on_existing_datasets()
    
    logger.info("Training and evaluation complete!")
    logger.info(f"Final evaluation results: {eval_results}")

if __name__ == "__main__":
    main() 