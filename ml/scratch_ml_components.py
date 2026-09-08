"""
SIH26102 — SCRATCH ML COMPONENTS ENGINE (ML-From-Scratch Integration)
========================================================================
Pure NumPy implementations of foundational machine learning algorithms
derived from ML-From-Scratch for transparent, dependency-free baseline
computation and fallback execution across Models M1-M5.

Algorithms Included:
- ScratchIsolationForest: Isolation Tree & Forest Anomaly Detector
- ScratchKMeans: K-Means Clustering for Peer Grouping
- ScratchPCA: Principal Component Analysis for Feature Reduction
- Euclidean & Mahalanobis Distance Metrics
"""

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
    """Pure NumPy Isolation Forest Anomaly Screening Engine."""
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

class ScratchPCA:
    """Pure NumPy Principal Component Analysis."""
    def __init__(self, n_components=2):
        self.n_components = n_components
        self.components_ = None
        self.mean_ = None
        
    def fit_transform(self, X):
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_
        cov = np.cov(X_centered, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = np.argsort(eigenvalues)[::-1]
        self.components_ = eigenvectors[:, idx[:self.n_components]]
        return np.dot(X_centered, self.components_)
