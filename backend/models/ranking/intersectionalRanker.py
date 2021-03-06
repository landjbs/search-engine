from scipy.spatial.distance import euclidean


def score_token_intersection(pageObj, tokenWeights):
    """
    Scores page by baseScore and score of multiple tokens
    """
    baseScore = pageObj.baseScore
    pageTokens = pageObj.knowledgeTokens
    knowledgeScore = 0

    for curToken, tokenWeight in tokenWeights.items():
        try:
            knowledgeScore += tokenWeight * pageTokens[curToken]
        except KeyError:
            knowledgeScore -= tokenWeight

    aggregateScore = baseScore + knowledgeScore

    return aggregateScore


def score_vector_intersection(pageObj, tokenScores, searchVec):
    """
    Scores page by baseScore, score of multiple tokens, and relationship
    with search vector
    """
    vecScore = (1 / euclidean(searchVec, pageObj.pageVec))

    tokenAndBaseScore = score_token_intersection(pageObj, tokenScores)
    aggregateScore = tokenAndBaseScore + vecScore

    return aggregateScore
