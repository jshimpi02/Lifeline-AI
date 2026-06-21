import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

vectorizer = HashingVectorizer(
    n_features=384,
    alternate_sign=False,
    norm=None
)


def embed(text: str):
    return vectorizer.transform([text]).toarray()[0]


def cosine_similarity(v1, v2):
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denom == 0:
        return 0.0

    return float(np.dot(v1, v2) / denom)