"""
Functions for all text processing involding knowledgeSet and knowledgeProcessor
built in models.knowledge.knowledgeBuilder.
"""

import re
import math
from numpy import log
import matplotlib.pyplot as plt
from collections import Counter


# dict mapping html divs to score  multiplier
divMultipiers = {'url':         5,
                'title':        6,
                'h1':           5,
                'h2':           4,
                'h3':           3,
                'lowHeaders':   2,
                'description':  3,
                'keywords':     3,
                'imageAlts':    3,
                'videoSRCs':    2,
                'all':          1}


def count_token(token, pageText):
    """
    Uses regexp to return number of times a token is used in pageText.
    Matches for tokens that are not parts of larger, uninterrupted words.
    Does not require a knowledgeProcessor.
    """
    return len(re.findall(f"(?<![a-zA-Z]){token}(?![a-zA-Z])", pageText, flags=re.IGNORECASE))


def url_count_token(token, url):
    """ Like count_token but no trailing non-chars neccessary """
    return len(re.findall(token, url, flags=re.IGNORECASE))


def find_rawTokens(inStr, knowledgeProcessor):
    """
    Finds set of tokens used in inStr without scoring or count.
    Used to tokenize search queries.
    Looks for both full tokens from knowledgeSet and single-word (sub) tokens
    """
    # use greedy matching of flashtext algorithm to find keywords
    greedyTokens = list(knowledgeProcessor.extract_keywords(inStr))
    # initialize list of all tokens with greedy tokens
    allTokens = greedyTokens.copy()
    # iterate over greedy tokens
    for token in greedyTokens:
        splitToken = token.split()
        if not (len(splitToken)==1):
            # iterate over white-space delimited words in each token
            for word in token.split():
                # find all tokens within the word and add to all tokens
                smallTokens = knowledgeProcessor.extract_keywords(word)
                allTokens += smallTokens
    return allTokens


def find_weighted_tokenCounts(inStr, knowledgeProcessor):
    """
    Finds dict mapping tokens used in inStr to number of times used.
    Does not normalize by length, div, or average frequency.
    Subtokens should be given 0.7 the weighting of full tokens
    """
    # get multi-occurence (!!!) list of the greedy tokens in inStr
    greedyTokens = knowledgeProcessor.extract_keywords(inStr)
    # get multi-occurence list of sub tokens in ' '-split greed tokens
    subTokens = []
    for token in greedyTokens:
        splitToken = token.split()
        if not (len(splitToken)==1):
            for word in splitToken:
                subTokens += knowledgeProcessor.extract_keywords(word)
    # get counts of sub tokens and normalize by 0.7
    subCounter = Counter(subTokens)
    weightedSubCounter = {token:(0.7*subCounter[token]) for token in subCounter}
    # combine greedTokens and normalized subTokens to get weighted token counts
    countedTokens = Counter(greedyTokens)
    countedTokens.update(weightedSubCounter)
    return countedTokens

def score_token(token, div, divText, divLen, divMultipier, tokensFound):
    """
    Scores individual token in div
    """

    ### FIND TOKEN FREQUENCY ###
    tokenNum = url_count_token(token, divText) if (div=='url') else count_token(token, divText)
    tokenFreq = tokenNum / divLen

    ### NORMALIZE TOKEN FREQUENCY ###
    # get term and document frequency of token in freqDict built on scraped data
    try:
        termFreq, docFreq = freqDict[token]
    except:
        termFreq, inverseDocFreq = 0, 0

    # normalize tokenFreq using a tf-idf schema
    normedFreq = tokenFreq - (1.2 * termFreq)

    # tokens with negative normedFreq will automatically have scores of 0
    if normedFreq <= 0:
        return 0

    # apply sublinear scaling normedFreq to reduce impact of token-spamming
    # scaledFreq = 1 + log(normedFreq)

    ### APPLY DIV-SPECIFIC SCORING MODELS ###
    if (div=='all'):
        ### TOKEN DISTRIBUTION SCORING ###
        # find start and end location of each token usage in the text
        tokenLocs = [(loc.span()[0], loc.span()[1]) for loc in re.finditer(token, divText, flags=re.IGNORECASE)]
        # get loc of first token usage
        firstUse = tokenLocs[0]
        # give benefit to pages with tokens appearing early


        ### RELATIVE LENGTH SCORING ###
        # get page length relative to average word count (assumed 700)
        relativeLen = divLen / 700
        # use sigmoid function on relative length to benefit longer pages with equal token freq to shorter (multiplier asymptotes at 1 and ~5)
        lengthMultiplier = (math.exp(0.25 * relativeLen) / (math.exp(0.25 * (relativeLen - 5.2)) + 1)) + 1
        normedFreq *= lengthMultiplier

    ### DIV MULTIPLICATION
    # apply div multiplier to boost tokens in important divs
    score = normedFreq * divMultipier

    return round(score, 3)


def find_scoredTokens(divText, div, knowledgeProcessor, freqDict, cutoff):
    """
    Args: Text of division being analyzed, name of division, processor to find
    tokens, dict of average word frequencies, score cutoff to include token in
    dict.
    Returns: Dict of tokens in divText mapping to score assigned by score_token
    """
    # find number of words in divText or (if its a url) number chars/(avg word length=5)
    if div=='url':
        divLen = len(divText) / 5
    else:
        divLen = len(divText.split())
    # find multiplier related to div
    divMultipier = divMultipiers[div]
    # use knowledgeProcessor to extract tokens from divText
    tokensFound = set(find_rawTokens(divText, knowledgeProcessor))

    # apply analyze_token to create dict mapping tokens to scores
    scoreDict = {token:score_token(token, div, divText, divLen, divMultipier, tokensFound)
                    for token in tokensFound}

    # filter scores below cuoff
    filteredScores = {token: score for token, score in scoreDict.items()
                        if score > cutoff}

    return filteredScores


def score_divDict(divDict, knowledgeProcessor, freqDict):
    """
    Args: Dict mapping page divisions to cleaned content (eg. {'title':'foo',
    'p':'hello world'}), knowledgeProcessor to use for matching, and dict of
    average knowledge token frequency.
    Returns: Dict mapping all knowledge tokens found in divDict to score
    determined by div found and relative frequency.
    """
    # initialize dict to hold tokens mapping to sum scores across all divs
    scoreDict = {}
    # iterate over divisions in divDict
    for div in divDict:
        # get text inside div
        divText = divDict[div]
        # get dict of tokens in divText and their scores
        divScores = find_scoredTokens(divText, div, knowledgeProcessor, freqDict, 0.005)
        # iterate over found tokens, adding their scores to the divDict
        for token in divScores:
            if token in scoreDict:
                scoreDict[token] += divScores[token]
            else:
                scoreDict.update({token:divScores[token]})
    return scoreDict
