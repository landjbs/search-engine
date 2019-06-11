"""
Functions for all text processing involding knowledgeSet and knowledgeProcessor
built in models.knowledge.knowledgeBuilder.
"""

import re
from flashtext import KeywordProcessor

knowledgeProcessor = KeywordProcessor(case_sensitive=False)
knowledgeProcessor.add_keyword('foo')

# keywordDict = {keyword:(len(re.findall(keyword, pageText, re.IGNORECASE))) for keyword in keywordsFound}

# def score_token(token, div):
#     """
#     Args: single knowledge token and html division where it occurred
#     Returns: score of token weighted by
#     """


def find_weightedTokens(divText, knowledgeProcessor):
    """
    Returns dict mapping knowledge tokens to score assigned by score_token
    """
    # find number of words in divText
    divLen = len(divText.split())
    # use knowledgeProcessor to extract tokens from page text
    tokensFound = knowledgeProcessor.extract_keywords(divText)
    # iterate over the tokens found
    for token in tokensFound:
        # find number of occurences of a token in divText
        tokenNum = len(re.findall(token, divText, flags=re.IGNORECASE))
        print(tokenNum)

def find_weighted_knowledge(divDict):
    """
    Args:
        divDict- Dict generated by crawlers.htmlAnalyzer mapping from
                 html divisions to the string of their contents.

    Returns: Single dict mapping from knowledgeTokens found to score assigned
    by weight

    Sample input: {'title':'foo bar', 'h1':'foo', 'p':'hello world'}
    """
    for div in divDict:
        divText = divDict[div]
        weightedTokens = find_weightedTokens(divText, knowledgeProcessor)

        # tokenDict = (find_tokens(divDict[div], knowledgeProcessor))
        # tokenDict = dict(map(lambda k : (k[0], k[1]/2), tokenDict.items()))
        # print(tokenDict)





find_weighted_knowledge({'title':'foo bar', 'h1':'foo', 'p':'hello world'})










pass
