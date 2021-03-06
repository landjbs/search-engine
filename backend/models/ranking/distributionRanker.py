"""
Ranks documents on the similarity between their parts. More diverse documents
will have higher scores for the same token frequency than less diverse documents.
"""

from numpy import mean
from scipy.spatial.distance import cosine, euclidean


def rank_distribution(baseVec, vecMatrix, n=5):
    """
    Args: baseVector of entire document, vecMatrix of vectorize_n_split(document)
    Gives document ranking on similarity between n-split document vectors.
    High diversityScore means that the page has more diversity between its
    compontents
    """
    # score cosine similarity between each chunk and base vec
    scores = [euclidean(curVec, baseVec) for curVec in vecMatrix]
    meanScore = mean(scores)
    # calculate distance between score distribution and uniform distribution around mean
    diversityScore = round(euclidean(scores, [meanScore for _ in range(n)]), 2)
    return diversityScore
