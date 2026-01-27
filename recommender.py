import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def get_recommendations(title, df):
    # Türleri ve özetleri birleştirip matematiksel modele sokacağız
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['genres']) # Şimdilik sadece türler
    
    # Cosine Similarity hesaplama
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # ... devamını beraber yazacağız ...