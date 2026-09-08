"""
SIH26102 — RESEARCH BENCHMARK & DIAGNOSTICS: SCRATCH ML COMPONENTS
======================================================================
Educational and diagnostic baseline implementations of machine learning algorithms
derived from ML-From-Scratch for benchmark comparison against Scikit-Learn production models.

Classification: RESEARCH BENCHMARK / DIAGNOSTIC TOOLING ONLY.
Canonical Production Model: Scikit-Learn IsolationForest (sklearn.ensemble.IsolationForest)
"""

import time
import numpy as np
import pandas as pd

class ScratchIsolationTree:
    """Single Isolation Tree constructed via random feature & split selection."""
    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.split_feature = None
        self.split_val = None
        self.left = None
        self.right = None
        self.size = 0
        
    def fit(self, X, current_depth=0):
        self.size = len(X)
        if current_depth >= self.max_depth or self.size <= 1:
            return self
            
        n_features = X.shape[1]
        feat_idx = np.random.randint(0, n_features)
        min_val, max_val = X[:, feat_idx].min(), X[:, feat_idx].max()
        
        if min_val == max_val:
            return self
            
        split_val = np.random.uniform(min_val, max_val)
        left_mask = X[:, feat_idx] < split_val
        
        self.split_feature = feat_idx
        self.split_val = split_val
        
        self.left = ScratchIsolationTree(self.max_depth).fit(X[left_mask], current_depth + 1)
        self.right = ScratchIsolationTree(self.max_depth).fit(X[~left_mask], current_depth + 1)
        return self
        
    def path_length(self, x, current_depth=0):
        if self.left is None or self.right is None:
            return current_depth + self._c(self.size)
            
        if x[self.split_feature] < self.split_val:
            return self.left.path_length(x, current_depth + 1)
        else:
            return self.right.path_length(x, current_depth + 1)
            
    def _c(self, n):
        if n <= 1:
            return 0
        if n == 2:
            return 1
        return 2 * (np.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)

class ScratchIsolationForest:
    """Pure NumPy Isolation Forest Baseline for Diagnostic Comparison."""
    def __init__(self, n_estimators=100, max_samples=256, contamination=0.05, random_state=42):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.random_state = random_state
        self.trees = []
        
    def fit(self, X):
        np.random.seed(self.random_state)
        n_samples = len(X)
        subsample_size = min(self.max_samples, n_samples)
        max_depth = int(np.ceil(np.log2(max(subsample_size, 2))))
        
        self.trees = []
        for _ in range(self.n_estimators):
            idx = np.random.choice(n_samples, subsample_size, replace=False)
            tree = ScratchIsolationTree(max_depth).fit(X[idx])
            self.trees.append(tree)
        return self
        
    def compute_anomaly_score(self, X):
        paths = np.zeros((len(X), len(self.trees)))
        for t_idx, tree in enumerate(self.trees):
            for i_idx, x in enumerate(X):
                paths[i_idx, t_idx] = tree.path_length(x)
                
        mean_path = np.mean(paths, axis=1)
        c_factor = 2 * (np.log(self.max_samples - 1) + 0.5772156649) - (2 * (self.max_samples - 1) / self.max_samples)
        scores = 2 ** (-mean_path / max(c_factor, 1e-8))
        return scores

def compare_scratch_vs_sklearn(X, sklearn_model):
    """
    Executes a side-by-side diagnostic benchmark comparing ScratchIsolationForest vs sklearn.IsolationForest.
    Calculates Pearson score correlation, top-k rank overlap, and runtime metrics.
    """
    t0 = time.time()
    scratch_model = ScratchIsolationForest(n_estimators=100, random_state=42).fit(X)
    scratch_scores = scratch_model.compute_anomaly_score(X)
    t_scratch = time.time() - t0
    
    t1 = time.time()
    sklearn_scores = -sklearn_model.decision_function(X)
    t_sklearn = time.time() - t1
    
    corr = float(np.corrcoef(scratch_scores, sklearn_scores)[0, 1])
    
    k = max(10, int(len(X) * 0.05))
    top_scratch = set(np.argsort(scratch_scores)[-k:])
    top_sklearn = set(np.argsort(sklearn_scores)[-k:])
    top_k_overlap = len(top_scratch.intersection(top_sklearn)) / float(k)
    
    return {
        'role': 'RESEARCH_BENCHMARK_DIAGNOSTIC',
        'score_correlation': round(corr, 4),
        'top_k_rank_overlap_pct': round(top_k_overlap * 100, 2),
        'scratch_runtime_sec': round(t_scratch, 4),
        'sklearn_runtime_sec': round(t_sklearn, 4),
        'canonical_model_status': 'Scikit-Learn IsolationForest is canonical production driver'
    }
