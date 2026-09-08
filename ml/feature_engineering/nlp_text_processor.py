"""
SIH26102 — ADVANCED NLP TEXT PROCESSING MODULE (funNLP Enhanced)
===================================================================
Integrates NLP text normalization, entity extraction, stop-word filtering,
and semantic text similarity metrics for Duplicate Work Linkage (M2)
and Inadmissible Work Eligibility Screening.

Audit Fencing:
- Preserves semantically meaningful MPLADS domain nouns (e.g., road, school, hospital,
  construction, hall, building, bridge, drainage, playground).
- Filters ONLY genuine administrative/location structural noise (e.g., no, number, gp, tq, dist, ward).
- Uses candidate-generation improvement hypothesis standard (unlabeled diagnostics).
"""

import os
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNNLP_STOPWORDS_DIR = os.path.join(BASE_DIR, "vendor", "funNLP", "data", "停用词")

# Strictly Administrative & Structural Noise Stopwords ONLY
# Semantically meaningful domain terms (road, school, hospital, hall, construction, etc.) are PRESERVED.
ADMINISTRATIVE_NOISE_STOPWORDS = {
    'of', 'at', 'in', 'near', 'to', 'for', 'and', 'with', 'the', 'a', 'an',
    'gp', 'gram', 'panchayat', 'tehsil', 'tq', 'dist', 'district', 'block', 'ward',
    'no', 'number', 'pry', 'sec', 'sl', 'sr', 'item'
}

def load_funnlp_stopwords():
    """Dynamically loads stop-words from funNLP data directory if present."""
    fun_words = set(ADMINISTRATIVE_NOISE_STOPWORDS)
    if os.path.exists(FUNNLP_STOPWORDS_DIR):
        for fname in os.listdir(FUNNLP_STOPWORDS_DIR):
            if fname.endswith(".txt"):
                fpath = os.path.join(FUNNLP_STOPWORDS_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            w = line.strip().lower()
                            # Only include structural/noise stopwords, avoiding English domain term overlap
                            if w and len(w) <= 3 and not re.search(r'\b(road|hall|work|well|pvm)\b', w):
                                fun_words.add(w)
                except Exception:
                    pass
    return fun_words

GLOBAL_STOPWORDS = load_funnlp_stopwords()

def clean_nlp_text(text):
    """
    Cleans and normalizes work description text.
    Removes non-alphanumeric punctuation, extra whitespace, and converts to lowercase.
    Applied BEFORE TF-IDF vectorization.
    """
    if pd.isna(text) or not str(text).strip():
        return ""
    s = str(text).lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_nlp_keywords(text, remove_stopwords=True):
    """
    Extracts key tokens from work description text after removing structural noise stopwords.
    Preserves meaningful domain nouns (construction, road, school, hospital, hall, building).
    """
    tokens = clean_nlp_text(text).split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in GLOBAL_STOPWORDS and len(t) > 1]
    return tokens

def compute_nlp_jaccard_similarity(text1, text2):
    """
    Computes Jaccard token similarity between two text strings.
    Candidate-generation diagnostic tool.
    """
    tokens1 = set(extract_nlp_keywords(text1))
    tokens2 = set(extract_nlp_keywords(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
        
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

def compute_batch_tfidf_similarity(text_list, ngram_range=(1, 2), min_df=1):
    """
    Computes TF-IDF N-gram cosine similarity matrix for a list of text descriptions.
    Cleaned text is processed BEFORE TF-IDF vectorization.
    """
    cleaned_texts = [clean_nlp_text(t) for t in text_list]
    vectorizer = TfidfVectorizer(ngram_range=ngram_range, min_df=min_df, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
    sim_matrix = cosine_similarity(tfidf_matrix)
    return sim_matrix, vectorizer

def extract_entity_mentions(text):
    """
    Extracts potential institution or entity types mentioned in work text.
    Note: Landmark mention in text does NOT automatically equal a funded object.
    Distinguishes location reference from project beneficiary.
    """
    clean_s = clean_nlp_text(text)
    
    mentions = {
        'is_educational': bool(re.search(r'\b(school|college|university|shala|vidyalaya|hostel)\b', clean_s)),
        'is_healthcare': bool(re.search(r'\b(hospital|clinic|phc|chc|dispensary|arogya)\b', clean_s)),
        'is_community': bool(re.search(r'\b(bhavan|mandapam|community hall|samudaya|sabhabhavana)\b', clean_s)),
        'is_religious': bool(re.search(r'\b(temple|mandir|masjid|mosque|church|gurudwara|matha|math)\b', clean_s)),
        'is_private_commercial': bool(re.search(r'\b(private|commercial|pvt|ltd|company|trust|society|shop|mall|hotel)\b', clean_s))
    }
    return mentions
