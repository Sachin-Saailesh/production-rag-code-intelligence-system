"""
RAG Evaluation using RAGAS framework.
Measures faithfulness, relevance, and context recall.
"""
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("Warning: RAGAS not installed. Evaluation features limited.")

class RAGEvaluator:
    """Evaluate RAG quality using RAGAS metrics"""
    
    def __init__(self):
        if not RAGAS_AVAILABLE:
            raise ImportError("RAGAS library required. Install with: pip install ragas datasets")
        
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision
        ]
    
    def evaluate_single(self, question: str, answer: str, contexts: List[str], 
                       ground_truth: Optional[str] = None) -> Dict[str, float]:
        """Evaluate a single QA pair"""
        
        data = {
            'question': [question],
            'answer': [answer],
            'contexts': [contexts],
        }
        
        if ground_truth:
            data['ground_truth'] = [ground_truth]
        
        dataset = Dataset.from_dict(data)
        
        # Use subset of metrics if no ground truth
        metrics_to_use = self.metrics if ground_truth else [faithfulness, answer_relevancy]
        
        results = evaluate(dataset, metrics=metrics_to_use)
        
        return {
            'faithfulness': results['faithfulness'],
            'answer_relevancy': results['answer_relevancy'],
            'context_recall': results.get('context_recall', None),
            'context_precision': results.get('context_precision', None)
        }
    
    def evaluate_batch(self, qa_pairs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Evaluate multiple QA pairs
        
        Args:
            qa_pairs: List of dicts with 'question', 'answer', 'contexts', optional 'ground_truth'
        """
        questions = []
        answers = []
        contexts = []
        ground_truths = []
        has_ground_truth = all('ground_truth' in qa for qa in qa_pairs)
        
        for qa in qa_pairs:
            questions.append(qa['question'])
            answers.append(qa['answer'])
            contexts.append(qa['contexts'])
            if has_ground_truth:
                ground_truths.append(qa['ground_truth'])
        
        data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts,
        }
        
        if has_ground_truth:
            data['ground_truth'] = ground_truths
        
        dataset = Dataset.from_dict(data)
        metrics_to_use = self.metrics if has_ground_truth else [faithfulness, answer_relevancy]
        
        results = evaluate(dataset, metrics=metrics_to_use)
        
        return pd.DataFrame(results)
    
    def get_summary_stats(self, results: pd.DataFrame) -> Dict[str, float]:
        """Get summary statistics from evaluation results"""
        return {
            'mean_faithfulness': results['faithfulness'].mean(),
            'mean_relevancy': results['answer_relevancy'].mean(),
            'mean_recall': results['context_recall'].mean() if 'context_recall' in results else None,
            'mean_precision': results['context_precision'].mean() if 'context_precision' in results else None,
        }
