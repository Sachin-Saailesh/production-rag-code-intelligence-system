import re
import math
from typing import List, Dict, Any, Tuple
from tqdm import tqdm

class SparseRetriever:
    """TF-IDF based sparse retriever"""
    
    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.doc_freq: Dict[int, int] = {}
        self.docs: List[Dict[str, Any]] = []
        self.doc_term_counts: List[Dict[int, int]] = []
        self.N = 0

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[A-Za-z_][A-Za-z0-9_\-\.]{1,64}", text)

    def index(self, chunks: List[Dict[str, Any]]):
        print("🧮 Building sparse index (TF-IDF)...")
        self.docs = chunks
        self.N = len(chunks)
        self.doc_term_counts = []
        self.vocab = {}
        self.doc_freq = {}
        
        for chunk in tqdm(chunks, desc="Sparse vocab"):
            terms = self._tokenize(chunk["content"].lower())
            counts: Dict[int, int] = {}
            seen_terms = set()
            for t in terms:
                if t not in self.vocab:
                    self.vocab[t] = len(self.vocab)
                tid = self.vocab[t]
                counts[tid] = counts.get(tid, 0) + 1
                if tid not in seen_terms:
                    self.doc_freq[tid] = self.doc_freq.get(tid, 0) + 1
                    seen_terms.add(tid)
            self.doc_term_counts.append(counts)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
        if self.N == 0:
            return []
            
        q_terms = self._tokenize(query.lower())
        q_counts: Dict[int, int] = {}
        for t in q_terms:
            if t in self.vocab:
                tid = self.vocab[t]
                q_counts[tid] = q_counts.get(tid, 0) + 1

        def tfidf(count, df):
            idf = math.log((self.N + 1) / (1 + df)) + 1.0
            return count * idf

        q_vec = {tid: tfidf(c, self.doc_freq.get(tid, 1)) for tid, c in q_counts.items()}
        q_norm = math.sqrt(sum(v*v for v in q_vec.values())) + 1e-8

        scores = []
        for i, counts in enumerate(self.doc_term_counts):
            dot = 0.0
            d_norm = 0.0
            for tid, c in counts.items():
                w = tfidf(c, self.doc_freq.get(tid, 1))
                d_norm += w*w
                if tid in q_vec:
                    dot += w * q_vec[tid]
            d_norm = math.sqrt(d_norm) + 1e-8
            sim = dot / (q_norm * d_norm)
            scores.append((sim, self.docs[i]))

        scores.sort(key=lambda x: -x[0])
        return scores[:top_k]
